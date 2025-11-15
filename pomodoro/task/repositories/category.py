"""Репозитории категорий."""

from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.task.models.categories import Category


class CategoryRepository(CRUDRepository):
    """Репозиторий кактегорий. Унаследован от базового репозитория."""

    def __init__(self, db_session: AsyncSession):
        """Инициализирует репозиторий категорий."""
        super().__init__(db_session=db_session, orm_model=Category)
