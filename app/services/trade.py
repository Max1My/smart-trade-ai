import datetime
import json
import logging
import sqlalchemy as sa

from app.models import Trade, TradeRecommendation
from app.repositories.db import DBRepository
from app.resources.database import Database
from app.schemas.market import AggregatedMarketData
from app.schemas.repository import RepositoryOutSchema
from app.schemas.trade import TradeSchema, TradeRecommendationSchema, TradeCreateSchema
from app.services.chat_gpt import ChatGPTService
from app.services.market import MarketService

logger = logging.getLogger(__name__)


class TradeService:
    db: Database
    repository_trade: DBRepository[Trade, TradeSchema]
    repository_trade_recommendation: DBRepository[TradeRecommendation, TradeRecommendationSchema]
    chatgpt_service: ChatGPTService
    market_service: MarketService

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

    async def analyze_and_save_recommendation(self, currency: str, minutes: int = 5) -> TradeRecommendationSchema:
        """
        Вызывает ChatGPT для анализа агрегированных данных и сохраняет результат как рекомендацию в базе.

        :param aggregated_data: Словарь с агрегированными данными за выбранный период.
        :param currency: Валютная пара, для которой проводится анализ.
        :return: Объект TradeRecommendation, сохранённый в базе данных.
        """
        try:
            async with self.db.session() as session:
                aggregated_data: AggregatedMarketData = await self.market_service.get_aggregated_market_data(
                    currency=currency,
                    minutes=minutes,
                    session=session
                )
                # Вызываем ChatGPT для анализа агрегированных данных.
                response = await self.chatgpt_service.analyze(aggregated_data.model_dump())
                # logger.info("Получен ответ от ChatGPT")
                #
                # # Пытаемся распарсить ответ как JSON.
                # try:
                #     parsed = json.loads(response)
                # except Exception as e:
                #     logger.error(f"Ошибка парсинга ответа ChatGPT: {e}")
                #     # Если парсинг не удался, используем весь текст ответа как рекомендацию,
                #     # а уровень уверенности ставим по умолчанию.
                #     parsed = {
                #         "recommended_action": response,
                #         "confidence": 0.5,
                #         "data": {}
                #     }
                #
                # stmt = sa.insert(TradeRecommendation).values(
                #     currency=currency,
                #     recommended=datetime.datetime.now(),
                #     recommended_action=parsed.get("recommended_action", ""),
                #     confidence=parsed.get("confidence", 0.0),
                #     data=parsed.get("data", {})
                # ).returning(TradeRecommendation)
                # recommendation: TradeRecommendationSchema = await self.repository_trade_recommendation.item(
                #     session=session,
                #     statement=stmt
                # )
                # logger.info(f"Рекомендация для {currency} сохранена в базе")
                # return recommendation

        except Exception as e:
            logger.error(f"Ошибка в анализе и сохранении рекомендации: {e}")
            raise

    async def add_trade(self, payload: TradeCreateSchema) -> TradeSchema:
        """
        Добавляет новую сделку в архив, используя данные из Pydantic-модели TradeCreateSchema.

        :param payload: Экземпляр TradeCreateSchema с данными сделки.
        :return: Объект Trade, сохранённый в базе.
        """
        async with self.db.session() as session:
            stmt = sa.insert(Trade).values(
                **payload.model_dump()
            ).returning(Trade)
            trade: TradeSchema = await self.repository_trade.item(session=session, statement=stmt)
            return trade

    async def get_trade_archive(self, currency: str, minutes: int = 1440) -> RepositoryOutSchema[TradeSchema]:
        """
        Извлекает сделки для указанной валютной пары за последние `minutes` минут.

        :param currency: Валютная пара, например, "BTCUSDT".
        :param minutes: Период выборки в минутах (по умолчанию 1440, т.е. сутки).
        :return: Список объектов Trade.
        """
        time_threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        async with self.db.session() as session:
            stmt = sa.select(Trade).where(
                Trade.currency == currency,
                Trade.opened >= time_threshold
            )
            trades: RepositoryOutSchema = await self.repository_trade.items(session=session, statement=stmt)
        return trades

    async def compile_archive_summary(self, currency: str, minutes: int = 1440) -> dict:
        """
        Компилирует сводную информацию из архива сделок для указанной валютной пары.

        Например, считает общее число сделок и средний PnL за указанный период.

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
