import asyncio
import logging
import time

from app.resources.bybit import BybitWebSocket
from app.resources.redis_client import RedisClient
from app.schemas.market import MarketCreateSchema
from app.services.market import MarketService

logger = logging.getLogger(__name__)

TOP_20_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT",
    "ADAUSDT", "DOGEUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT",
    "AVAXUSDT", "LINKUSDT", "ATOMUSDT", "XMRUSDT",
    "ETCUSDT", "BCHUSDT", "NEARUSDT", "APTUSDT", "FILUSDT"
]


class WebSocketService:
    def __init__(
            self,
            market_service: MarketService,
            bybit_ws: BybitWebSocket,
            redis_client: RedisClient,
            symbols=None
    ):
        self.market_service = market_service
        self.bybit_ws = bybit_ws
        self.redis_client = redis_client
        self.symbols = symbols or TOP_20_SYMBOLS
        self.is_running = True

        # Убираем прямое хранение loop (или создаём сами, если нужно).
        self.loop = asyncio.get_event_loop()

        self.message_buffer = []
        self.batch_size = 10

    async def handle_message(self, message: dict):
        """Обрабатывает входящие данные и записывает их в БД"""
        if "data" in message:
            try:
                data = message["data"]
                if isinstance(data, list):
                    if not data:
                        logger.warning(f"⚠ Пустой массив данных: {message}")
                        return
                    data = data[0]  # Берем первый элемент списка

                payload = MarketCreateSchema(
                    currency=message["topic"].split(".")[1],
                    kind=message["topic"],
                    data=data
                )
                await self.market_service.create(payload)
            except Exception as e:
                logger.error(f"⚠ Ошибка обработки сообщения: {e}\nmessage: {message}")

    def _handle_sync_message(self, message: dict):
        """
        Обертка для вызова add_to_redis в event loop.
        Если bybit_ws вызывает этот колбэк из другого потока,
        то нужен call_soon_threadsafe.
        """
        self.loop.call_soon_threadsafe(asyncio.create_task, self.add_to_redis(message))

    async def add_to_redis(self, message: dict):
        """Добавление сообщений в пакет"""
        self.message_buffer.append(message)
        if len(self.message_buffer) >= self.batch_size:
            await self.flush_to_redis()

    async def flush_to_redis(self):
        """Запись пакета в Redis"""
        if self.message_buffer:
            try:
                logger.info(f'Отправляю сообщения в redis')
                # Вместо time.sleep(5) используем асинхронную паузу
                await asyncio.sleep(5)
                await self.redis_client.add_to_queue_batch('websocket_messages', self.message_buffer)
                self.message_buffer.clear()
                logger.info('Сообщения отправлены успешно')
            except Exception as e:
                logger.error(f"Ошибка записи в Redis: {e}")
        else:
            logger.debug("Буфер пустой, нет данных для записи в Redis.")

    async def process_redis_queue(self):
        """Фоновая задача для обработки очереди Redis и записи данных в БД"""
        while self.is_running:
            try:
                message = await self.redis_client.pop_from_queue('websocket_messages')
                if message:
                    await self.handle_message(message)
            except Exception as e:
                logger.error(f"⚠ Ошибка при обработке очереди Redis: {e}")
            await asyncio.sleep(1)

    async def start(self):
        """Запускает подписку на WebSocket и обработку сообщений из Redis"""
        # Подключаемся к Redis
        await self.redis_client.connect()

        # Запускаем фоновую задачу обработки очереди Redis
        asyncio.create_task(self.process_redis_queue())

        # Подключаемся к WebSocket и подписываемся на нужные топики
        while self.is_running:
            try:
                for symbol in self.symbols:
                    self.bybit_ws.subscribe_orderbook(symbol=symbol, callback=self._handle_sync_message)
                    self.bybit_ws.subscribe_trades(symbol=symbol, callback=self._handle_sync_message)
                    self.bybit_ws.subscribe_candles(symbol=symbol, interval=1, callback=self._handle_sync_message)
                    self.bybit_ws.subscribe_liquidations(symbol=symbol, callback=self._handle_sync_message)
                    await asyncio.sleep(5)

                logger.info(f"✅ Подписаны на {len(self.symbols)} валютных пар")

                # Основной цикл удерживает задачу "живой"
                while self.is_running:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"⚠ Ошибка WebSocket: {e}. Переподключение через 5 секунд...")
                await asyncio.sleep(5)

    async def stop(self):
        """Останавливает WebSocket и фоновую задачу"""
        self.is_running = False
        # Если нужно, отписываемся от топиков и закрываем WebSocket
        # self.bybit_ws.close()  # в зависимости от реализации

        # Закрываем Redis-подключение (если это нужно по логике вашего RedisClient)
        try:
            await self.redis_client.redis.close()
        except Exception as e:
            logger.error(f"Ошибка закрытия Redis: {e}")
