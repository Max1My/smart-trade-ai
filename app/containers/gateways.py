"""Gateways container."""
import aiogram
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Provider, Singleton, Resource

from app.resources.bybit import BybitWebSocket, BybitRest
from app.resources.database import Database
from app.resources.redis_client import RedisClient


class GatewaysContainer(DeclarativeContainer):
    """Gateways container."""

    config: Configuration = Configuration()

    db: Provider[Database] = Singleton(
        Database,
        url_rw=config.db.url_rw,
        url_ro=config.db.url_ro,
        echo=config.db.echo,
        pool_size=50,
        pool_timeout=30,
        pool_recycle=3600,
        max_overflow=20,
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
    redis: Provider[RedisClient] = Singleton(
        RedisClient,
        password=config.redis.password
    )
