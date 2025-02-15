class TradeRepository:
    def __init__(self):
        self.data = {}

    def save_orderbook(self, symbol: str, data: dict):
        """Сохранение данных стакана"""
        self.data[symbol] = {"orderbook": data}

    def save_candles(self, symbol: str, data: dict):
        """Сохранение данных свечей"""
        self.data[symbol]["candles"] = data

    def save_trade(self, symbol: str, data: dict):
        """Сохранение истории трейдов"""
        self.data[symbol]["trades"] = data
