"""Репозитории задач."""

from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.tasks import Task


class TaskRepository(CRUDRepository):
    """Репозиторий задач. Унаследован от базового репозитория."""

    def __init__(self, db_session: AsyncSession):
        """Инициализируем репозиторий здач."""
        super().__init__(db_session, Task)
