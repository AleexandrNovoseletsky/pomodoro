"""Category dependencies.

Dependency injection setup for category-related components. Provides
factory functions for creating category repositories and services with
proper dependency management for FastAPI integration.
"""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.services.category_service import CategoryService


async def get_category_repository() -> CategoryRepository:
    """Create and return category repository instance.

    Returns:     CategoryRepository: Repository instance configured with
    database session maker     for performing category database
    operations.

    Note:     Uses application-wide async session maker for database
    connectivity.     Repository is created per request for proper
    connection management.
    """
    return CategoryRepository(sessionmaker=async_session_maker)


async def get_category_service(
    category_repo: Annotated[
        CategoryRepository, Depends(dependency=get_category_repository)
    ],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> CategoryService:
    """Create and return category service instance with dependencies.

    Args:     category_repo: Injected category repository for data
    access     media_service: Injected media service for file operations

    Returns:     CategoryService: Service instance with all dependencies
    resolved     for handling category business logic and operations.

    Note:     Service is created per request with properly injected
    dependencies     following dependency injection pattern for
    testability and modularity.
    """
    return CategoryService(
        category_repo=category_repo, media_service=media_service
    )
