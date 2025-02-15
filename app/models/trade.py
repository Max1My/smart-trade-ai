"""."""

import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TradeRecommendation(Base):
    """
    Модель для хранения рекомендаций по сделкам, полученных от AI (например, ChatGPT).

    Атрибуты:
        id (int): Уникальный идентификатор записи.
        currency (str): Валютная пара, для которой сделана рекомендация.
        recommended (datetime): Время, когда была сделана рекомендация.
        recommended_action (str): Рекомендованное действие (например, открыть длинную или короткую позицию).
        confidence (float): Уровень уверенности в рекомендации.
        data (dict): Дополнительные данные, связанные с рекомендацией (например, технические индикаторы, свечные паттерны).
    """
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(sa.String(20))
    recommended: Mapped[datetime.datetime] = mapped_column(sa.DateTime)
    recommended_action: Mapped[str] = mapped_column(sa.String)
    confidence: Mapped[float] = mapped_column(sa.Numeric)
    data: Mapped[dict] = mapped_column(sa.JSON)


class Trade(Base):
    """
    Модель для хранения информации о сделках.

    Атрибуты:
        id (int): Уникальный идентификатор сделки.
        currency (str): Валютная пара, для которой была открыта сделка.
        opened (datetime): Время открытия сделки.
        side (str): Направление сделки (например, long или short).
        quantity (float): Количество купленных или проданных единиц.
        entry_price (float): Цена открытия позиции.
        leverage (float): Используемое плечо.
        stop_loss (float): Уровень стоп-лосса.
        take_profit (float): Уровень тейк-профита.
        status (str): Статус сделки (например, открыта или закрыта).
        exit_price (float): Цена закрытия позиции.
        pnl (float): Прибыль или убыток от сделки.
    """
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    currency: Mapped[str] = mapped_column(sa.String(20))
    opened: Mapped[datetime.datetime] = mapped_column(sa.DateTime)
    side: Mapped[str] = mapped_column(sa.String(4))
    quantity: Mapped[float] = mapped_column(sa.Numeric)
    entry_price: Mapped[float] = mapped_column(sa.Numeric)
    leverage: Mapped[float] = mapped_column(sa.Numeric)
    stop_loss: Mapped[float] = mapped_column(sa.Numeric)
    take_profit: Mapped[float] = mapped_column(sa.Numeric)
    status: Mapped[str] = mapped_column(sa.String)
    exit_price: Mapped[float] = mapped_column(sa.Numeric)
    pnl: Mapped[float] = mapped_column(sa.Numeric)
