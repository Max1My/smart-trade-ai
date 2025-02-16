"""Database resource."""

import contextlib
import logging
import typing

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class Database:
    """Database."""

    _engine_rw: AsyncEngine
    _engine_ro: AsyncEngine
    _factory_rw: sessionmaker
    _factory_ro: sessionmaker

    def __init__(
            self,
            url_rw: str,
            url_ro: str | None = None,
            echo: bool = False,
            pool_size: int = 5,
            pool_timeout: int = 30,
            pool_recycle: int = 1800,
            max_overflow: int = 10,
            expire_on_commit: bool = False,
            pool_pre_ping: bool = True,
            application_name: str = "",
    ):
        """."""
        application_name = application_name or const.APP
        url_ro = url_ro or url_rw
        self._engine_rw = create_async_engine(
            url_rw,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            connect_args={
                "server_settings": {"application_name": application_name},
            },
        )
        self._factory_rw = sessionmaker(
            self._engine_rw,
            expire_on_commit=expire_on_commit,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )
        self._engine_ro = create_async_engine(
            url_ro,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            connect_args={
                "server_settings": {"application_name": application_name},
            },
        )
        self._factory_ro = sessionmaker(
            self._engine_ro,
            expire_on_commit=expire_on_commit,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )

    @contextlib.asynccontextmanager
    async def session_rw(
            self, session: AsyncSession | None = None
    ) -> typing.AsyncGenerator[AsyncSession, None]:
        """Session factory."""
        if session:
            yield session
        else:
            session: AsyncSession = self._factory_rw()
            try:
                yield session
            finally:
                await session.close()

    @contextlib.asynccontextmanager
    async def session_ro(
            self, session: AsyncSession | None = None
    ) -> typing.AsyncGenerator[AsyncSession, None]:
        """Session factory."""
        if session:
            yield session
        else:
            session: AsyncSession = self._factory_ro()
            try:
                yield session
            finally:
                await session.close()

    # For backward compatibility
    session = session_rw
