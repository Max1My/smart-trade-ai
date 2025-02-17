"""Services container."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    DependenciesContainer, Provider, Singleton,
)

from app.containers.gateways import GatewaysContainer
from app.containers.repositories import RepositoriesContainer
from app.services.bybit_stream import WebSocketService
from app.services.market import MarketService
from app.services.trade import TradeService


class ServicesContainer(DeclarativeContainer):
    """Services container."""

    config: Configuration = Configuration()
    repositories: RepositoriesContainer = DependenciesContainer()
    gateways: GatewaysContainer = DependenciesContainer()

    trade: Provider[TradeService] = Singleton(
        TradeService,
        bybit_websocket=gateways.bybit_websocket,
        bybit_rest=gateways.bybit_rest,
        repository=repositories.trade,
    )
    market: Provider[MarketService] = Singleton(
        MarketService,
        db=gateways.db,
        repository=repositories.market
    )

    bybit_stream: Provider[WebSocketService] = Singleton(
        WebSocketService,
        market_service=market,
        bybit_ws=gateways.bybit_websocket,
        redis_client=gateways.redis,
    )
