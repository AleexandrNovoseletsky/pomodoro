"""Репозитории категорий."""

from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.categories import Category


class CategoryRepository(CRUDRepository):
    """Репозиторий кактегорий. Унаследован от базового репозитория."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Инициализирует репозиторий категорий."""
        super().__init__(sessionmaker=sessionmaker, orm_model=Category)
