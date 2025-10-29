from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db_session
from repositories import CategoryRepository
from services import CategoryService


async def get_category_repository(
    db: Session = Depends(get_db_session),
) -> CategoryRepository:
    return CategoryRepository(db)


async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(repository=category_repo)
