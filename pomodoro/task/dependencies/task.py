"""Task dependencies.

Dependency injection configuration for task-related components. Provides
factory functions for creating task repositories, cache repositories,
services, and resource retrieval with proper dependency management.
"""

from typing import Annotated

from fastapi import Depends

from pomodoro.database.accesor import async_session_maker
from pomodoro.database.cache.accesor import get_cache_session
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.models.tasks import Task
from pomodoro.task.repositories.cache_tasks import TaskCacheRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.task.services.task_service import TaskService


async def get_task_repository() -> TaskRepository:
    """Create and return task repository instance.

    Returns:     TaskRepository: Repository instance configured with
    database session maker     for performing task database operations.

    Note:     Uses application-wide async session maker for consistent
    database connectivity.     Repository is created per request for
    proper connection lifecycle management.
    """
    return TaskRepository(sessionmaker=async_session_maker)


async def get_cache_task_repository() -> TaskCacheRepository | None:
    """Create and return task cache repository instance.

    Returns:     TaskCacheRepository | None: Cache repository instance
    for Redis operations     or None if cache session cannot be
    established.

    Note:     Uses async generator pattern to properly manage Redis
    connection lifecycle.     Returns None if cache is unavailable to
    allow graceful degradation.
    """
    async for cache_session in get_cache_session():
        return TaskCacheRepository(cache_session=cache_session)
    return None


async def get_task_service(
    task_repo: Annotated[
        TaskRepository, Depends(dependency=get_task_repository)
    ],
    cache_repo: Annotated[
        TaskCacheRepository, Depends(dependency=get_cache_task_repository)
    ],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> TaskService:
    """Create and return task service instance with all dependencies.

    Args:     task_repo: Injected task repository for database
    operations     cache_repo: Injected cache repository for Redis
    operations     media_service: Injected media service for file
    management

    Returns:     TaskService: Fully configured service instance for
    handling task business logic,     caching, and media operations.

    Note:     All dependencies are automatically resolved by FastAPI's
    dependency injection system.     Service supports graceful
    degradation when cache is unavailable.
    """
    return TaskService(
        task_repo=task_repo, cache_repo=cache_repo, media_service=media_service
    )


async def get_task_resource(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    """Retrieve single task entity by ID.

    Args:     task_id: Unique identifier of the task to retrieve
    task_service: Injected task service for data retrieval

    Returns:     Task: Task entity model instance

    Raises:     ObjectNotFoundError: If task with specified ID doesn't
    exist

    Note:     Commonly used as a dependency in endpoints that require
    specific task context.     Performs existence validation
    automatically.
    """
    return await task_service.get_one_object(object_id=task_id)
