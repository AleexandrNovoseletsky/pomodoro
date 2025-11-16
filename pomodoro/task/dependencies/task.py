"""Зависомости задач."""

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


async def get_task_repository(
) -> TaskRepository:
    """Получение репозитория задач."""
    return TaskRepository(sessionmaker=async_session_maker)


async def get_cache_task_repository() -> TaskCacheRepository | None:
    """Получение кэщ-репозитория задач."""
    async for cache_session in get_cache_session():
        return TaskCacheRepository(cache_session=cache_session)
    return None


async def get_task_service(
    task_repo: Annotated[
        TaskRepository, Depends(dependency=get_task_repository)
        ],
    cache_repo: Annotated[TaskCacheRepository, Depends(
        dependency=get_cache_task_repository
        )],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> TaskService:
    """Получение сервиса задач."""
    return TaskService(
        task_repo=task_repo,
        cache_repo=cache_repo,
        media_service=media_service
        )


async def get_task_resource(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],

) -> Task:
    """Получение одной задачи."""
    return await task_service.get_one_object(object_id=task_id)
