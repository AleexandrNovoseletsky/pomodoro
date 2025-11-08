from sqlalchemy.ext.asyncio import AsyncSession

from app.task.models.categories import Category
from app.core.repositories.base_crud import CRUDRepository


class CategoryRepository(CRUDRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Category)
