"""."""

import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Market(Base):
    """
    Модель для хранения данных о текущем состоянии рынка.

    Атрибуты:
        id (int): Уникальный идентификатор записи.
        currency (str): Валютная пара, например, BTC/USDT.
        created (datetime): Время создания записи.
        kind (str): Тип данных (например, рыночные данные, данные о ценах и т.д.).
        data (dict): Данные о рынке в формате JSON (например, данные стакана, цены, ордера).
    """
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(sa.String(20))
    created: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=datetime.datetime.now(), nullable=False)
    kind: Mapped[str] = mapped_column(sa.String)
    data: Mapped[dict] = mapped_column(sa.JSON)
