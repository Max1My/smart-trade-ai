import asyncio
import logging

from app.resources.bybit import BybitWebSocket
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
    def __init__(self, market_service: MarketService, bybit_ws: BybitWebSocket, symbols=None):
        self.market_service = market_service
        self.bybit_ws = bybit_ws
        self.symbols = symbols or TOP_20_SYMBOLS
        self.is_running = True
        self.loop = asyncio.get_event_loop()

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
        """Обертка для вызова handle_message в event loop"""
        self.loop.call_soon_threadsafe(asyncio.create_task, self.handle_message(message))

    async def start(self):
        """Запускает подписку на WebSocket с обработкой ошибок"""
        while self.is_running:
            try:
                # Подписки
                for symbol in self.symbols:
                    self.bybit_ws.subscribe_orderbook(symbol, self._handle_sync_message)
                    self.bybit_ws.subscribe_candles(symbol, interval=1, callback=self._handle_sync_message)
                    self.bybit_ws.subscribe_trades(symbol, self._handle_sync_message)
                    self.bybit_ws.subscribe_liquidations(symbol, self._handle_sync_message)

                logger.info(f"✅ Подписаны на {len(self.symbols)} валютных пар")

                while self.is_running:
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"⚠ Ошибка WebSocket: {e}. Переподключение через 5 секунд...")
                await asyncio.sleep(5)  # Заменил time.sleep(5) на await asyncio.sleep(5)

    async def stop(self):
        """Останавливает WebSocket"""
        self.is_running = False
