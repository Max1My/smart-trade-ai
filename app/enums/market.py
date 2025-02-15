import enum


class MarketKindEnums(enum.StrEnum):
    """."""
    ORDERBOOK = "orderbook"
    KLINE = "kline"
    TRADE_HISTORY = "trade_history"
    LIQUIDATION = "liquidation"