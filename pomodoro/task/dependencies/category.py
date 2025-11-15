"""Зависимости категорий."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.database.accesor import get_db_session
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.services.category_service import CategoryService


async def get_category_repository(
    db: Annotated[AsyncSession, Depends(dependency=get_db_session)]
) -> CategoryRepository:
    """Получение репозитория категорий."""
    return CategoryRepository(db_session=db)


async def get_category_service(
    category_repo: Annotated[
        CategoryRepository,
        Depends(dependency=get_category_repository)
        ]
) -> CategoryService:
    """Получение сервиса категорий."""
    return CategoryService(category_repo=category_repo)
