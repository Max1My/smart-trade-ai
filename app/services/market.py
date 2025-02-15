"""."""

import sqlalchemy as sa

from app.repositories.db import DBRepository
from app.resources.database import Database
from app.schemas.market import MarketSchema, MarketCreateSchema
from app.models.market import Market


class MarketService:
    db: Database
    repository: DBRepository[Market, MarketSchema]

    def __init__(
            self,
            db: Database,
            repository: DBRepository[Market, MarketSchema]
    ) -> None:
        self.db = db
        self.repository = repository

    @staticmethod
    def compare_orderbooks(prev_data: dict, new_data: dict) -> dict:
        """
        Сравнивает два снимка стакана.
        Возвращает разницу в формате {'bids': {'added': [], 'removed': [], 'updated': []}, 'asks': {...}}
        """

        def process_side(prev: list, new: list):
            """Сравнивает стороны стакана (bids или asks)"""
            prev_dict = {price: float(size) for price, size in prev}  # Преобразуем в словарь {цена: объем}
            new_dict = {price: float(size) for price, size in new}

            added = [(price, size) for price, size in new_dict.items() if price not in prev_dict]
            removed = [(price, size) for price, size in prev_dict.items() if price not in new_dict]
            updated = [(price, size) for price, size in new_dict.items()
                       if price in prev_dict and prev_dict[price] != size]

            return {'added': added, 'removed': removed, 'updated': updated}

        return {
            'bids': process_side(prev_data['b'], new_data['b']),
            'asks': process_side(prev_data['a'], new_data['a']),
        }

    async def create(self, payload: MarketCreateSchema) -> MarketSchema:
        async with self.db.session() as session:
            stmt = (
                sa.Select(Market)
                .filter_by(currency=payload.currency, kind=payload.kind)
                .order_by(Market.created.desc())
                .limit(1)
            )
            last_record: MarketSchema = await self.repository.item(session=session, statement=stmt)

            # Если в БД ещё нет данных, просто создаём первую запись
            if not last_record:
                stmt = sa.insert(Market).values(**payload.model_dump()).returning(Market)
                market: MarketSchema = await self.repository.item(session=session, statement=stmt)
                await session.commit()
                return market

            if "b" in payload.data and "a" in payload.data:
                diff = self.compare_orderbooks(prev_data=last_record.data, new_data=payload.data)

                # Если нет изменений, не записываем дубликат
                if not any(diff[key][change] for key in ["bids", "asks"] for change in ["added", "removed", "updated"]):
                    return last_record

            # Сохраняем новый снимок, если есть изменения
            stmt = sa.insert(Market).values(**payload.model_dump()).returning(Market)
            market = await self.repository.item(session=session, statement=stmt)
            await session.commit()
        return market


