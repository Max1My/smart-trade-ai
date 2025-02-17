"""."""
import logging

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from app.repositories.db import DBRepository
from app.resources.database import Database
from app.schemas.market import MarketSchema, MarketCreateSchema
from app.models.market import Market

logger = logging.getLogger(__name__)


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

    async def create(self, payload: MarketCreateSchema):
        async with self.db.session() as session:
            stmt = (
                insert(Market)
                .values(payload.model_dump())
            )
            # Выполняем запрос без использования scalars, так как он не возвращает строки.
            await session.execute(stmt)
            await session.commit()
