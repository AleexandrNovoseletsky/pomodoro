"""Task repositories.

Provides data access layer for task entities using the base CRUD
repository pattern. Handles database operations for task management with
proper session management.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.tasks import Task


class TaskRepository(CRUDRepository[Task]):
    """Task repository inheriting from base CRUD repository.

    Provides data access operations for Task entities with full CRUD
    functionality. Inherits all base operations from CRUDRepository with
    Task-specific configuration.

    Attributes:
        sessionmaker: Async session factory for database
                      operations
        orm_model: Task model class for ORM operations
    """

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initialize task repository with database session.

        Args:
            sessionmaker: Async session factory for database
                          connectivity
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=Task)
