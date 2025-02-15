"""."""
import datetime

from app.enums.market import MarketKindEnums
from app.schemas.base import BaseSchema


class MarketSchema(BaseSchema):
    """."""
    id: int
    currency: str
    created: datetime.datetime
    kind: str
    data: dict


class MarketCreateSchema(BaseSchema):
    currency: str
    kind: str
    data: dict
