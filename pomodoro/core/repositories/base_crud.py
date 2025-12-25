"""Base CRUD repository.

Provides a generic asynchronous CRUD (Create, Read, Update, Delete)
repository implementation for SQLAlchemy models. Serves as the
foundation for all domain-specific repositories with consistent data
access patterns.
"""

from datetime import UTC, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError

ORMModel = TypeVar("ORMModel")


class CRUDRepository(Generic[ORMModel]):
    """Asynchronous CRUD repository with generic type support.

    Provides standard Create, Read, Update, Delete operations for
    SQLAlchemy models with proper session management, transaction
    handling, and type safety.

    Attributes:
        sessionmaker: Async session factory for database operations
        orm_model: SQLAlchemy model class for ORM operations
    """

    def __init__(
            self, sessionmaker: async_sessionmaker, orm_model: type[ORMModel]
    ):
        """Initialize repository with database session.

        Args:
            sessionmaker:
                Async session factory for database
                connectivity
            orm_model:
                SQLAlchemy model class that this
                repository manages
        """
        self.sessionmaker = sessionmaker
        self.orm_model = orm_model

    async def create_object(self, data: BaseModel) -> ORMModel:
        """Create a new model instance in the database.

        Persists a new entity using provided Pydantic schema data within
        a transaction and returns the created instance.

        Args:
            data: Pydantic schema containing field values for
                  creation

        Returns:
            Created model instance with database-generated
            fields

        Note:
            Automatically refreshes the instance to include
            database-generated values like auto-increment IDs and
            default field values
        """
        async with self.sessionmaker() as session:
            async with session.begin():
                obj = self.orm_model(**data.model_dump())
                session.add(obj)
            await session.refresh(obj)
            return obj

    async def get_object(self, object_id: int) -> ORMModel | None:
        """Retrieve a single model instance by primary key.

        Args:
            object_id: Primary key identifier of the target object

        Returns:
            Model instance if found, None if no object exists
            with given ID

        Note:
             Uses scalar_one_or_none() to safely handle missing
             objects without raising exceptions for non-existent IDs
        """
        async with self.sessionmaker() as session:
            # External users from suppliers may not have digital ID.
            pk_attr: str | int = self.orm_model.id

            result = await session.execute(
                select(self.orm_model).where(pk_attr == object_id)
            )
            return result.scalar_one_or_none()

    async def get_one_object_or_raise(self, object_id: int) -> ORMModel:
        """Retrieve a single model or raise.

        Args:
            object_id: Primary key identifier of the target object

        Returns:
            Model instance if found

        Raises:
            ObjectNotFoundError: If no object exists
        """
        obj = await self.get_object(object_id=object_id)
        if obj is None:
            raise ObjectNotFoundError(object_id=object_id)
        return obj

    async def get_all_objects(self) -> list[ORMModel]:
        """Retrieve all model instances from the database table.

        Returns:
            List containing all model instances in the table

        Note:
            Returns empty list if no records exist in the table
        """
        async with self.sessionmaker() as session:
            result = await session.execute(select(self.orm_model))
            return list(result.scalars().all())

    async def update_object(
        self, object_id: int, update_data: BaseModel
    ) -> ORMModel | None:
        """Update an existing model instance with partial data.

        Modifies specified fields of an existing entity while preserving
        unchanged fields and automatically updating the modification
        timestamp.

        Args:
            object_id:
                Primary key identifier of the object to update
            update_data:
                Pydantic schema containing fields to modify

        Returns:
            Updated model instance if found, None if object
            doesn't exist

        Note:
            Uses exclude_unset=True to only update provided
            fields, enabling partial updates without affecting
            unspecified fields
        """
        async with self.sessionmaker() as session:
            async with session.begin():
                # External users from suppliers may not have digital ID.
                pk_attr: str | int = self.orm_model.id

                result = await session.execute(
                    select(self.orm_model).where(pk_attr == object_id)
                )
                obj = result.scalars().one_or_none()
                if obj is None:
                    return None

                for key, value in update_data.model_dump(
                    exclude_unset=True
                ).items():
                    setattr(obj, key, value)

                # Update modification timestamp manually
                obj.updated_at = datetime.now(UTC)

            await session.refresh(obj)
            return obj

    async def delete_object(self, object_id: int) -> bool:
        """Permanently delete a model instance from the database.

        Args:
            object_id: Primary key identifier of the object to
                       delete

        Returns:
            True if object was successfully deleted, False if
            object didn't exist

        Note:
            This is a hard delete operation that permanently
            removes the record.
            Consider soft deletion using is_active
            flag for data preservation.
        """
        async with self.sessionmaker() as session:
            # External users from suppliers may not have digital ID.
            pk_attr: str | int = self.orm_model.id

            async with session.begin():
                result = await session.execute(
                    delete(self.orm_model).where(pk_attr == object_id)
                )
            return result.rowcount > 0  # type: ignore[attr-defined]
