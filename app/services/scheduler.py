import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from app.enums.market import TOP_20_SYMBOLS
from app.schemas.market import AggregatedMarketData
from app.schemas.trade import TradeRecommendationSchema
from app.services.chat_gpt import ChatGPTService
from app.services.market import MarketService
from app.services.trade import TradeService

logger = logging.getLogger(__name__)


class SchedulerService:
    trade_service: TradeService
    scheduler: AsyncIOScheduler

    def __init__(
            self,
            trade_service: TradeService,
            scheduler: AsyncIOScheduler
    ):
        """
        :param trade_service: Сервис для получения агрегированных рыночных данных (MarketService или его обёртка).
        :param scheduler: Сервис, который интегрирует вызов ChatGPT и сохранение рекомендаций.
        """
        self.trade_service = trade_service
        self.scheduler = scheduler

    async def short_term_analysis(self):
        """
        Краткосрочный анализ: анализ данных за последние 5 минут.
        """
        for currency in TOP_20_SYMBOLS:
            try:
                logger.info(f"[Краткосрочный] Запуск анализа рыночных данных для {currency}")
                recommendation: TradeRecommendationSchema = await self.trade_service.analyze_and_save_recommendation(currency, minutes=5)
                logger.info(f"[Краткосрочный] Рекомендация для {currency} получена и сохранена: {recommendation.id}")
            except Exception as e:
                logger.error(f"[Краткосрочный] Ошибка анализа для {currency}: {e}")

    async def long_term_analysis(self):
        """
        Долгосрочный анализ: анализ данных за последние сутки.
        """
        for currency in TOP_20_SYMBOLS:
            try:
                logger.info(f"[Долгосрочный] Запуск анализа рыночных данных для {currency}")
                # Например, агрегируем данные за последние 1440 минут (24 часа)
                recommendation: TradeRecommendationSchema = await self.trade_service.analyze_and_save_recommendation(currency, minutes=1440)
                logger.info(f"[Долгосрочный] Рекомендация для {currency} получена и сохранена: {recommendation.id}")
            except Exception as e:
                logger.error(f"[Долгосрочный] Ошибка анализа для {currency}: {e}")

    def start(self):
        """
        Запускает планировщик APScheduler с двумя заданиями:
        - Краткосрочный анализ каждые 5 минут.
        - Долгосрочный анализ раз в сутки.
        """
        self.scheduler.add_job(self.short_term_analysis, trigger=IntervalTrigger(minutes=5), id="short_term")
        self.scheduler.add_job(self.long_term_analysis, trigger=IntervalTrigger(minutes=1440), id="long_term")
        self.scheduler.start()
        logger.info("APScheduler запущен: краткосрочный анализ каждые 5 минут, долгосрочный анализ раз в сутки.")

    def shutdown(self):
        """
        Останавливает планировщик.
        """
        self.scheduler.shutdown()
        logger.info("APScheduler остановлен.")
