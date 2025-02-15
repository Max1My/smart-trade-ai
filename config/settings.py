"""Project settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent


class BybitSettings(BaseSettings):
    """Bybit settings."""
    api_key: str = ""
    api_secret: str = ""


class DBSettings(BaseSettings):
    """Database settings."""

    url_rw: str = "postgresql+asyncpg://dev:dev@localhost:5432/mydatabase"
    url_ro: str = "postgresql+asyncpg://dev:dev@localhost:5432/mydatabase"
    echo: bool = False


class Settings(BaseSettings):
    """CTR settings."""

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / "config" / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    debug: bool = False
    db: DBSettings = DBSettings()
    bybit: BybitSettings = BybitSettings()
