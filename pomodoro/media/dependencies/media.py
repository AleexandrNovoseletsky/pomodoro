"""Зависимости медиа."""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.media.models.files import Files
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.services.media_service import MediaService


async def get_media_repository() -> MediaRepository:
    """Получение репозитория медиа."""
    return MediaRepository(sessionmaker=async_session_maker)


async def get_media_service(
    media_repo: Annotated[
        MediaRepository, Depends(dependency=get_media_repository)
        ]
) -> MediaService:
    """Получение сервиса медиа."""
    return MediaService(media_repo=media_repo)


async def get_media_resource(
    file_id: int,
    media_service: Annotated[MediaService, Depends(get_media_service)]
) -> Files:
    """Получение одного файла."""
    return await media_service.get_one_object(object_id=file_id)
