import datetime
import json
import logging
import sqlalchemy as sa

from app.models import Trade, TradeRecommendation
from app.repositories.db import DBRepository
from app.resources.database import Database
from app.schemas.market import AggregatedMarketData
from app.schemas.repository import RepositoryOutSchema
from app.schemas.trade import TradeSchema, TradeRecommendationSchema, TradeCreateSchema, \
    TradeRecommendationsCreateSchema
from app.services.chat_gpt import ChatGPTService
from app.services.market import MarketService

logger = logging.getLogger(__name__)


class TradeService:
    def __init__(
            self,
            db: Database,
            chatgpt_service: ChatGPTService,
            repository_trade: DBRepository[Trade, TradeSchema],
            repository_trade_recommendation: DBRepository[TradeRecommendation, TradeRecommendationSchema],
            market_service: MarketService
    ):
        self.db = db
        self.chatgpt_service = chatgpt_service
        self.repository_trade = repository_trade
        self.repository_trade_recommendation = repository_trade_recommendation
        self.market_service = market_service

    async def analyze_and_save_final_recommendation(self, currency: str, minutes: int = 5) -> TradeRecommendationSchema:
        """
        Проводит анализ агрегированных рыночных данных с учетом предыдущей рекомендации (если она существует)
        и сохраняет новую торговую рекомендацию в базе данных.

        Алгоритм:
         1. Извлекаем агрегированные данные за последние `minutes` минут через MarketService.
         2. Пытаемся получить последнюю запись из TradeRecommendation для указанной валютной пары.
         3. Если предыдущая рекомендация найдена, объединяем её данные с текущими агрегированными данными и
            вызываем ChatGPT для дополнительного анализа.
         4. Если предыдущей рекомендации нет, выполняется обычный анализ.
         5. Ответ от ChatGPT парсится (ожидается формат JSON).
         6. На основе парсенного ответа создается объект TradeRecommendationsCreateSchema, который используется
            для вставки новой записи в базу.

        :param currency: Валютная пара, например, "BTCUSDT".
        :param minutes: Интервал выборки агрегированных данных (по умолчанию 5 минут).
        :return: Сохраненная рекомендация в виде TradeRecommendationSchema.
        """
        try:
            async with self.db.session() as session:
                # 1. Получаем агрегированные данные
                aggregated_data: AggregatedMarketData = await self.market_service.get_aggregated_market_data(
                    currency=currency,
                    minutes=minutes,
                    session=session
                )
                aggregated_dict = aggregated_data.model_dump()

                # 2. Пытаемся получить последнюю рекомендацию
                stmt = (
                    sa.select(TradeRecommendation)
                    .where(TradeRecommendation.currency == currency)
                    .order_by(TradeRecommendation.recommended.desc())
                    .limit(1)
                )
                last_rec = await self.repository_trade_recommendation.item(session=session, statement=stmt)

                # 3. Если предыдущая рекомендация существует, объединяем данные для дополнительного анализа
                if last_rec:
                    prev_rec_dict = last_rec.model_dump()
                    logger.info("Обнаружена предыдущая рекомендация. Выполняется дополнительный анализ.")
                    response: dict = await self.chatgpt_service.final_analysis(
                        primary_analysis=prev_rec_dict,
                        secondary_analysis=aggregated_dict
                    )
                else:
                    logger.info("Предыдущая рекомендация не найдена. Выполняется первичный анализ.")
                    response: dict = await self.chatgpt_service.analyze(aggregated_dict)

                logger.info("Получен ответ от ChatGPT для финального анализа.")


                # 5. Создаем полезную нагрузку с использованием TradeRecommendationsCreateSchema
                rec_payload = TradeRecommendationsCreateSchema(
                    currency=currency,
                    recommended=datetime.datetime.now(),
                    recommended_action=response.get("recommended_action", ""),
                    confidence=response.get("index_gpt", {}).get("growth_probability", 0.0),
                    # Добавляем вероятность роста
                    data=response  # Сохраняем все данные из ответа ChatGPT
                )

                # 6. Сохраняем новую рекомендацию в базе
                stmt_insert = (
                    sa.insert(TradeRecommendation)
                    .values(**rec_payload.model_dump())
                    .returning(TradeRecommendation)
                )
                new_rec: TradeRecommendationSchema = await self.repository_trade_recommendation.item(
                    session=session,
                    statement=stmt_insert
                )
                logger.info(f"Новая рекомендация для {currency} сохранена в базе.")
                await session.commit()
            return new_rec

        except Exception as e:
            logger.error(f"Ошибка в анализе и сохранении финальной рекомендации: {e}")
            raise

    async def add_trade(self, payload: TradeCreateSchema) -> TradeSchema:
        """
        Добавляет новую сделку в архив, используя данные из Pydantic-модели TradeCreateSchema.

        :param payload: Экземпляр TradeCreateSchema с данными сделки.
        :return: Схема сохраненной сделки (TradeSchema).
        """
        async with self.db.session() as session:
            stmt = (
                sa.insert(Trade)
                .values(**payload.model_dump())
                .returning(Trade)
            )
            trade: TradeSchema = await self.repository_trade.item(
                session=session,
                statement=stmt
            )
            return trade

    async def get_trade_archive(self, currency: str, minutes: int = 1440) -> RepositoryOutSchema[TradeSchema]:
        """
        Извлекает сделки для указанной валютной пары за последние `minutes` минут.

        :param currency: Валютная пара, например, "BTCUSDT".
        :param minutes: Интервал выборки (по умолчанию 1440 минут, то есть сутки).
        :return: Репозиторный вывод (RepositoryOutSchema) с объектами TradeSchema.
        """
        time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        async with self.db.session() as session:
            stmt = sa.select(Trade).where(
                Trade.currency == currency,
                Trade.opened >= time_threshold
            )
            trades: RepositoryOutSchema[TradeSchema] = await self.repository_trade.items(
                session=session,
                statement=stmt
            )
        return trades

    async def compile_archive_summary(self, currency: str, minutes: int = 1440) -> dict:
        """
        Компилирует сводную информацию из архива сделок для указанной валютной пары.
        Например, рассчитывает общее число сделок и средний PnL за указанный период.

        :param currency: Валютная пара.
        :param minutes: Период выборки в минутах.
        :return: Словарь со сводной информацией.
        """
        trades: RepositoryOutSchema[TradeSchema] = await self.get_trade_archive(currency, minutes)
        total_trades = trades.total
        avg_pnl = sum(trade.pnl for trade in trades.items) / total_trades if total_trades > 0 else 0
        summary = {
            "currency": currency,
            "total_trades": total_trades,
            "average_pnl": avg_pnl,
        }
        return summary