"""Зависимости категорий."""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.services.category_service import CategoryService


async def get_category_repository(
) -> CategoryRepository:
    """Получение репозитория категорий."""
    return CategoryRepository(sessionmaker=async_session_maker)


async def get_category_service(
    category_repo: Annotated[
        CategoryRepository,
        Depends(dependency=get_category_repository)
        ],
    media_service: Annotated[MediaService, Depends(get_media_service)]
) -> CategoryService:
    """Получение сервиса категорий."""
    return CategoryService(
        category_repo=category_repo, media_service=media_service
        )
