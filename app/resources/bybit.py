from pybit.unified_trading import WebSocket
from pybit.unified_trading import HTTP


class BybitWebSocket:
    def __init__(self):
        """Инициализация WebSocket с нужным адресом"""
        self.ws = WebSocket(testnet=False, channel_type="linear")

    def subscribe_orderbook(self, symbol: str, callback, depth: int = 50):
        """Подписка на стакан"""
        self.ws.orderbook_stream(symbol=symbol, callback=callback, depth=depth)

    def subscribe_candles(self, symbol: str, interval: int, callback):
        """Подписка на свечи"""
        self.ws.kline_stream(symbol=symbol, interval=interval, callback=callback)

    def subscribe_trades(self, symbol: str, callback):
        """Подписка на историю сделок"""
        self.ws.trade_stream(symbol=symbol, callback=callback)

    def subscribe_liquidations(self, symbol: str, callback):
        """Подписка на ликвидации"""
        self.ws.liquidation_stream(symbol=symbol, callback=callback)

    def subscribe_derivatives(self, symbol: str, callback):
        """Подписка на данные по деривативам (Futures & Options API)"""
        topic = f"derivatives.{symbol}"
        self.ws.subscribe(topic, callback, symbol)


class BybitRest:
    def __init__(self, api_key: str, api_secret: str):
        self.rest_client = HTTP(api_key=api_key, api_secret=api_secret, testnet=False)

    def get_balance(self):
        """Получение баланса"""
        return self.rest_client.get_wallet_balance()

    def place_order(self, symbol: str, side: str, qty: float, price: float, order_type: str = "Limit"):
        """Открытие ордера"""
        return self.rest_client.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            qty=qty,
            price=price,
            orderType=order_type,
            timeInForce="GoodTillCancel"
        )

    def close_order(self, order_id: str):
        """Закрытие ордера"""
        return self.rest_client.cancel_order(category="linear", orderId=order_id)
