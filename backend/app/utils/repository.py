from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.config.db import Base


class SQLAlchemyRepository[ModelType: Base]:
    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _apply_filters(self, statement: Any, filters: dict[str, Any]) -> Any:
        for field, value in filters.items():
            if value is not None:
                statement = statement.where(getattr(self.model, field) == value)
        return statement

    async def add(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get(self, identifier: Any) -> ModelType | None:
        return await self.session.get(self.model, identifier)

    async def list(
        self, order_by: ColumnElement[Any] | None = None, **filters: Any
    ) -> Sequence[ModelType]:
        statement = self._apply_filters(select(self.model), filters)
        if order_by is not None:
            statement = statement.order_by(order_by)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def count_all(self, **filters: Any) -> int:
        statement = self._apply_filters(select(func.count()).select_from(self.model), filters)
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()
