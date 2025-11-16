from datetime import UTC, datetime
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped


class HasId(Protocol):
    """Протокол для ORM-моделей с полем id и updated_at."""
    id: Mapped[int]
    updated_at: Mapped[datetime]


T = TypeVar("T", bound=HasId)


class CRUDRepository[T]:
    """Асинхронный CRUD-репозиторий с использованием sessionmaker."""

    def __init__(self, sessionmaker: async_sessionmaker, orm_model: type[Any]):
        self.sessionmaker = sessionmaker
        self.orm_model = orm_model

    async def create_object(self, data: BaseModel) -> T:
        async with self.sessionmaker() as session:
            async with session.begin():
                obj = self.orm_model(**data.model_dump())
                session.add(obj)
            await session.refresh(obj)
            return obj

    async def get_object(self, object_id: int) -> T | None:
        async with self.sessionmaker() as session:
            pk_attr: Any = self.orm_model.id
            result = await session.execute(
                select(self.orm_model).where(pk_attr == object_id)
            )
            return result.scalar_one_or_none()

    async def get_all_objects(self) -> list[T]:
        async with self.sessionmaker() as session:
            result = await session.execute(select(self.orm_model))
            return list(result.scalars().all())

    async def update_object(
            self, object_id: int, update_data: BaseModel
            ) -> T | None:
        async with self.sessionmaker() as session:
            pk_attr: Any = self.orm_model.id
            result = await session.execute(
                select(self.orm_model).where(pk_attr == object_id)
            )
            obj = result.scalar_one_or_none()
            if obj is None:
                return None

            for key, value in update_data.model_dump(
                exclude_unset=True
                    ).items():
                setattr(obj, key, value)

            # Обновляем метку времени вручную
            obj.updated_at = datetime.now(UTC)

            async with session.begin():
                session.add(obj)  # безопасно добавить для коммита
            await session.refresh(obj)
            return obj

    async def delete_object(self, object_id: int) -> bool:
        async with self.sessionmaker() as session:
            pk_attr: Any = self.orm_model.id
            async with session.begin():
                result = await session.execute(
                    delete(self.orm_model).where(pk_attr == object_id)
                )
            return result.rowcount > 0  # type: ignore[attr-defined]
