"""."""
import datetime

from app.schemas.base import BaseSchema


class BalanceSchema(BaseSchema):
    id: int
    event: datetime.datetime
    balance: float
    percentage_drop: float
    action_taken: str
