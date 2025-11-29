"""Media dependencies."""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.schemas.media import ResponseFileSchema
from pomodoro.media.services.media_service import MediaService


async def get_media_repository() -> MediaRepository:
    """Get media repository.

    Returns:     Media repository.
    """
    return MediaRepository(sessionmaker=async_session_maker)


async def get_media_service(
    media_repo: Annotated[
        MediaRepository, Depends(dependency=get_media_repository)
    ],
) -> MediaService:
    """Get media service.

    Args:     media_repo: Depends on media repository.

    Returns:     Media service.
    """
    return MediaService(media_repo=media_repo)


async def get_media_resource(
    file_id: int,
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> ResponseFileSchema:
    """Get one media object.

    Args:     file_id: ID of the file you are looking for.
    media_service: Depends on the media service.

    Returns:     Pydantic validate File response schema.
    """
    return await media_service.get_one_object(object_id=file_id)
