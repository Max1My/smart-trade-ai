"""Gateways container."""
import aiogram
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Provider, Singleton, Resource

from app.resources.bybit import BybitWebSocket, BybitRest
from app.resources.database import Database


class GatewaysContainer(DeclarativeContainer):
    """Gateways container."""

    config: Configuration = Configuration()

    db: Provider[Database] = Singleton(
        Database,
        url_rw=config.db.url_rw,
        url_ro=config.db.url_ro,
        echo=config.db.echo,
        pool_size=10,
        max_overflow=10,
        expire_on_commit=False,
        pool_pre_ping=True,
        application_name="smart_trade_ai",
    )
    bybit_websocket: Provider[BybitWebSocket] = Singleton(
        BybitWebSocket
    )
    bybit_rest: Provider[BybitRest] = Singleton(
        BybitRest,
        api_key=config.bybit.api_key,
        api_secret=config.bybit.api_secret
    )
    bot: Provider[aiogram.Bot] = Singleton(aiogram.Bot, token=config.bot.token)
