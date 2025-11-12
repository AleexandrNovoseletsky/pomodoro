"""Репозитории категорий."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.base_crud import CRUDRepository
from app.task.models.categories import Category


class CategoryRepository(CRUDRepository):
    """Репозиторий кактегорий. Унаследован от базового репозитория."""

    def __init__(self, db_session: AsyncSession):
        """Инициализирует репозиторий категорий."""
        super().__init__(db_session, Category)
