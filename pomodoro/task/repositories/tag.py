"""Tag repositories.

Provides data access layer for tag entities using the base CRUD
repository pattern. Handles database operations for tag management with
proper session management.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.tags import Tag


class TagRepository(CRUDRepository[Tag]):
    """Tag repository inheriting from base CRUD repository.

    Provides data access operations for Tag entities with full CRUD
    functionality. Inherits all base operations from CRUDRepository with
    Tag-specific configuration.

    Attributes:
        sessionmaker: Async session factory for database
                      operations
        orm_model: Tag model class for ORM operations
    """

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initialize tag repository with database session.

        Args:
            sessionmaker: Async session factory for database
                          connectivity
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=Tag)

    @staticmethod
    async def get_by_ids(ids: list[int]) -> list[Tag]:
        """Get multiple tags by their IDs.

        Args:
            ids: List of tag IDs to retrieve.

        Returns:
            List of Tag objects.
        """
        async with async_sessionmaker as session:
            stmt = select(Tag).where(Tag.id.in_(ids))
            result = await session.execute(stmt)
            return list(result.scalars())
