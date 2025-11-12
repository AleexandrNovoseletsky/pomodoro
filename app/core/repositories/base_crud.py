"""Базовый CRUD-репозиторий над SQLAlchemy с небольшими утилитами.

Модуль содержит репозиторий, используемый сервисами проекта.
Важно: методы помечены как async, но внутри выполняют синхронные
операции с SQLAlchemy-сессией. Не вызывайте их параллельно на одной
сессии без внешней синхронизации.
"""

from datetime import UTC, datetime
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped


class HasId(Protocol):
    """Протокол для ORM-моделей с полем id и updated_at.

    Используется для типизации возвращаемых ORM-объектов.
    """

    id: Mapped[int]
    updated_at: Mapped[datetime]


T = TypeVar("T", bound=HasId)


class CRUDRepository[T]:
    """Минимальный CRUD-репозиторий, оборачивающий SQLAlchemy-сессию.

    Класс не управляет транзакциями автоматически — это делает внешний код.
    """

    def __init__(self, db_session: AsyncSession, orm_model: type[Any]):
        """Инициализируем базовый репозитоий."""
        self.db_session = db_session
        self.orm_model = orm_model

    async def create_object(self, data: BaseModel) -> T:
        """Создать ORM-объект из Pydantic-модели и вернуть созданный объект.

        Метод создаёт экземпляр модели на основе data.model_dump().
        """
        obj = self.orm_model(**data.model_dump())
        # Добавляем объект в сессию и коммитим асинхронно
        self.db_session.add(obj)
        await self.db_session.commit()
        await self.db_session.refresh(obj)
        return obj

    async def get_object(self, object_id: int) -> T | None:
        """Получить объект по id или вернуть None, если не найден.

        Возвращает ORM-экземпляр (не Pydantic-схему).
        """
        # Используем getattr для обращения к class-атрибуту id, чтобы
        # избежать ошибок статической типизации: у Type[T] mypy не видит
        # дескрипторы SQLAlchemy как доступные атрибуты класса.
        pk_attr: Any = self.orm_model.id
        result = await self.db_session.execute(
            select(self.orm_model).where(pk_attr == object_id)
        )
        return result.scalar_one_or_none()

    async def get_all_objects(self) -> list[T]:
        """Вернуть все объекты ORM для данной модели.

        Используется сервисами для пакетного получения сущностей.
        """
        result = await self.db_session.execute(select(self.orm_model))
        return list(result.scalars().all())

    async def update_object(
        self, object_id: int, update_data: BaseModel
    ) -> T | None:
        """Изминение объекта БД."""
        pk_attr: Any = self.orm_model.id
        result = await self.db_session.execute(
            select(self.orm_model).where(pk_attr == object_id)
        )
        obj = result.scalar_one_or_none()

        if obj is None:
            return None

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        # Обновляем метку времени вручную
        obj.updated_at = datetime.now(UTC)
        await self.db_session.commit()
        await self.db_session.refresh(obj)
        return obj

    async def delete_object(self, object_id: int) -> bool:
        """Удаление объекта БД."""
        pk_attr: Any = self.orm_model.id
        result = await self.db_session.execute(
            delete(self.orm_model).where(pk_attr == object_id)
        )
        await self.db_session.commit()
        # Явно приводим результат к булеву значению
        return result.rowcount > 0  # type: ignore[attr-defined]
