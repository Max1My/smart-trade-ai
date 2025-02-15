"""Repositories container."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Provider, Factory

from app.models.balance import Balance
from app.models.trade import Trade, TradeRecommendation
from app.repositories.db import DBRepository
from app.models.market import Market
from app.schemas.balance import BalanceSchema
from app.schemas.market import MarketSchema
from app.schemas.trade import TradeSchema, TradeRecommendationSchema


class RepositoriesContainer(DeclarativeContainer):
    """Repositories container."""

    config: Configuration = Configuration()

    market: Provider[DBRepository[Market, MarketSchema]] = Factory(
        DBRepository[Market, MarketSchema], model=Market, schema=MarketSchema
    )
    balance: Provider[DBRepository[Balance, BalanceSchema]] = Factory(
        DBRepository[Balance, BalanceSchema], model=Balance, schema=BalanceSchema
    )
    trade: Provider[DBRepository[Trade, TradeSchema]] = Factory(
        DBRepository[Trade, TradeSchema], model=Trade, schema=TradeSchema
    )
    trade_recommendation: Provider[DBRepository[TradeRecommendation, TradeRecommendationSchema]] = Factory(
        DBRepository[TradeRecommendation, TradeRecommendationSchema], model=TradeRecommendation,
        schema=TradeRecommendationSchema
    )
