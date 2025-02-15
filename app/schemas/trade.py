"""."""
import datetime

from app.schemas.base import BaseSchema


class TradeRecommendationSchema(BaseSchema):
    """."""
    id: int
    currency: str
    recommended: datetime.datetime
    recommended_action: str
    confidence: float
    data: dict


class TradeSchema(BaseSchema):
    """."""
    id: int
    currency: str
    opened: datetime.datetime
    side: str
    quantity: float
    entry_price: float
    leverage: float
    stop_loss: float
    take_profit: float
    status: str
    exit_price: float
    pnl: float
