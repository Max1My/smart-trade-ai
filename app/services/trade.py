import logging

from app.repositories.trade import TradeRepository
from app.resources.bybit import BybitWebSocket, BybitRest

logger = logging.getLogger(__name__)


class TradeService:
    def __init__(
            self,
            bybit_websocket: BybitWebSocket,
            bybit_rest: BybitRest,
            repository: TradeRepository
    ):
        self.bybit_websocket = bybit_websocket
        self.bybit_rest = bybit_rest
        self.repository = repository

    def start_streams(self, symbol: str):
        """Запускаем подписки на Bybit WebSocket"""
        self.bybit_websocket.subscribe_orderbook(symbol, self.handle_orderbook)
        self.bybit_websocket.subscribe_candles(symbol, 1, self.handle_candles)
        self.bybit_websocket.subscribe_trades(symbol, self.handle_trades)

    def handle_orderbook(self, message):
        """Обрабатываем данные стакана"""
        symbol = message["data"]["s"]
        self.repository.save_orderbook(symbol, message)
        logger.info(f"Orderbook updated for {symbol}")

    def handle_candles(self, message):
        """Обрабатываем свечные данные"""
        symbol = message["data"]["s"]
        self.repository.save_candles(symbol, message)
        logger.info(f"Candles updated for {symbol}")

    def handle_trades(self, message):
        """Обрабатываем историю сделок"""
        symbol = message["data"]["s"]
        self.repository.save_trade(symbol, message)
        logger.info(f"Trade history updated for {symbol}")
