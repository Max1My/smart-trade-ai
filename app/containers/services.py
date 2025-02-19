"""Services container."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import (
    Configuration,
    DependenciesContainer, Provider, Singleton,
)

from app.containers.gateways import GatewaysContainer
from app.containers.repositories import RepositoriesContainer
from app.services.bybit_stream import WebSocketService
from app.services.chat_gpt import ChatGPTService
from app.services.market import MarketService
from app.services.scheduler import SchedulerService
from app.services.trade import TradeService


class ServicesContainer(DeclarativeContainer):
    """Services container."""

    config: Configuration = Configuration()
    repositories: RepositoriesContainer = DependenciesContainer()
    gateways: GatewaysContainer = DependenciesContainer()

    market: Provider[MarketService] = Singleton(
        MarketService,
        db=gateways.db,
        repository=repositories.market
    )
    chatgpt_service: Provider[ChatGPTService] = Singleton(
        ChatGPTService,
        api_key=config.chatgpt.api_key
    )

    trade: Provider[TradeService] = Singleton(
        TradeService,
        db=gateways.db,
        repository_trade=repositories.trade,
        repository_trade_recommendation=repositories.trade_recommendation,
        market_service=market,
        chatgpt_service=chatgpt_service
    )

    bybit_stream: Provider[WebSocketService] = Singleton(
        WebSocketService,
        market_service=market,
        bybit_ws=gateways.bybit_websocket,
        redis_client=gateways.redis,
    )

    scheduler: Provider[SchedulerService] = Singleton(
        SchedulerService,
        scheduler=gateways.scheduler,
        trade_service=trade
    )
