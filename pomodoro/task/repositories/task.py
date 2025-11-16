"""Репозитории задач."""

from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.tasks import Task


class TaskRepository(CRUDRepository):
    """Репозиторий задач. Унаследован от базового репозитория."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Инициализируем репозиторий здач."""
        super().__init__(sessionmaker=sessionmaker, orm_model=Task)
