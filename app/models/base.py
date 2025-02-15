"""."""

import typing

from pydantic.alias_generators import to_snake
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr


class BaseModel(DeclarativeBase):
    """Base model class."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """."""
        return to_snake(cls.__name__)


class Base(BaseModel, DeclarativeBase):
    """Base model class."""

    metadata = MetaData(schema="smart_trade_ai")


TModel = typing.TypeVar("TModel", bound=BaseModel)
