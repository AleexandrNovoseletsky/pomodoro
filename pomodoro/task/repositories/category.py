"""Category repositories.

Provides data access layer for category entities using the base CRUD
repository pattern. Handles database operations for category management
with proper session management.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.categories import Category


class CategoryRepository(CRUDRepository):
    """Category repository inheriting from base CRUD repository.

    Provides data access operations for Category entities with full CRUD
    functionality. Inherits all base operations from CRUDRepository with
    Category-specific configuration.

    Attributes:     sessionmaker: Async session factory for database
    operations     orm_model: Category model class for ORM operations
    """

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initialize category repository with database session.

        Args:     sessionmaker: Async session factory for database
        connectivity
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=Category)
