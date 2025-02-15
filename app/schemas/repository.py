"""Base repository schemas."""

import typing

import pydantic

from app.schemas.base import TSchema


class RepositoryOutSchema(pydantic.BaseModel, typing.Generic[TSchema]):
    """Base repository output schema."""

    limit: int
    offset: int
    total: int
    items: list[TSchema] = []

    @property
    def page(self) -> int:
        """Page."""
        return int(self.offset / self.limit) + 1

    @property
    def size(self) -> int:
        """Size."""
        return self.limit
