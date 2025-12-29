"""Tag dependencies.

Dependency injection setup for tag-related components.
Provides factory functions for creating tag repositories
and services with proper dependency management
for FastAPI integration.
"""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.tag import TagRepository
from pomodoro.task.services.tag_service import TagService


async def get_tag_repository() -> TagRepository:
    """Create and return tag repository instance.

    Returns:
        TagRepository: Repository instance configured with
                       database session maker for performing
                       tag database operations.

    Note:
        Uses application-wide async session maker for database
        connectivity.
        Repository is created per request for proper
        connection management.
    """
    return TagRepository(sessionmaker=async_session_maker)


async def get_tag_service(
    tag_repo: Annotated[
        TagRepository, Depends(dependency=get_tag_repository)
    ],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> TagService:
    """Create and return tag service instance with dependencies.

    Args:
        tag_repo: Injected tag repository for data access
        media_service: Injected media service for file operations

    Returns:
        TagService: Service instance with all dependencies resolved
                    for handling tag business logic and operations.

    Note:
        Service is created per request with properly injected
        dependencies following dependency injection pattern for
        testability and modularity.
    """
    return TagService(
        tag_repo=tag_repo, media_service=media_service
    )
