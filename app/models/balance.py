"""."""

import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Balance(Base):
    """
    Модель для хранения данных о балансе и предупреждениях о просадке.

    Атрибуты:
        id (int): Уникальный идентификатор записи.
        event (datetime): Время события (например, падение баланса).
        balance (float): Текущий баланс на момент события.
        percentage_drop (float): Процентное снижение баланса.
        action_taken (str): Описание предпринятых действий (например, остановка торговли).
    """
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    event: Mapped[datetime.datetime] = mapped_column(sa.DateTime)
    balance: Mapped[float] = mapped_column(sa.Numeric)
    percentage_drop: Mapped[float] = mapped_column(sa.Numeric)
    action_taken: Mapped[str] = mapped_column(sa.String)
