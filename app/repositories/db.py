"""."""

import typing

import pydantic
import sqlalchemy as sa
from sqlalchemy.engine.result import Result, ScalarResult
from sqlalchemy.ext.asyncio.session import AsyncSession


from app.models.base import TModel
from app.schemas.base import TSchema
from app.schemas.repository import RepositoryOutSchema

TStatement = sa.sql.Select | sa.Update | sa.Insert | sa.Delete


class DBRepository(typing.Generic[TModel, TSchema]):
    """Database repository."""

    model: TModel
    schema: TSchema

    def __init__(self, model: TModel, schema: TSchema):
        """Init db repository."""
        self.model = model
        self.schema = schema

    @property
    def list_schema_adapter(self) -> pydantic.TypeAdapter:
        """."""
        return pydantic.TypeAdapter(list[self.schema])

    async def item(
            self,
            session: AsyncSession,
            statement: TStatement,
    ) -> TSchema | None:
        """."""
        item = await self.scalar(session, statement)
        if item:
            return self.schema.model_validate(item)

    async def items(
            self,
            session: AsyncSession,
            statement: sa.Select | sa.Update,
            limit: int | None = None,
            offset: int = 0,
    ) -> RepositoryOutSchema[TSchema]:
        """."""
        items, total = await self._items(session, statement, limit, offset)
        return RepositoryOutSchema[TSchema](
            items=self.list_schema_adapter.validate_python(items),
            total=total,
            limit=limit or total,
            offset=offset,
        )

    async def scalar(
            self,
            session: AsyncSession,
            statement: TStatement,
    ) -> TModel | None:
        """."""
        session_result: Result = await session.execute(statement)
        return session_result.scalar()

    async def scalars(
            self,
            session: AsyncSession,
            statement: TStatement,
    ) -> ScalarResult[TModel]:
        """."""
        session_result: Result = await session.execute(statement)
        return session_result.scalars()

    async def total(self, session: AsyncSession, statement: sa.Select) -> int:
        """."""
        statement_total = statement.limit(None).offset(None).order_by(None)
        session_result: Result = await session.execute(
            sa.Select(sa.func.count()).select_from(
                statement_total,
            ),  # type: ignore[arg-type]
        )
        return session_result.scalar() or 0

    def limit_and_offset(
            self,
            statement: sa.Select,
            limit: int | None = None,
            offset: int = 0,
    ) -> sa.Select:
        """."""
        if limit and limit > 0:
            statement = statement.limit(limit)
        return statement.offset(offset)

    async def _items(
            self,
            session: AsyncSession,
            statement: TStatement,
            limit: int | None = None,
            offset: int = 0,
            unique: bool = False,
    ) -> tuple[typing.Sequence, int]:
        total: int = await self.total(session, statement)
        if total > 0 and limit:
            statement = self.limit_and_offset(statement, limit, offset)
        scalar_result = await self.scalars(session, statement)
        if unique:
            scalar_result = scalar_result.unique().all()
        return scalar_result.all(), total
