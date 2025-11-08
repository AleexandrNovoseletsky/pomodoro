from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.accesor import get_db_session
from app.task.repositories.category import CategoryRepository
from app.task.services.category_service import CategoryService


async def get_category_repository(
    db: AsyncSession = Depends(get_db_session),
) -> CategoryRepository:
    return CategoryRepository(db)


async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(category_repo=category_repo)
