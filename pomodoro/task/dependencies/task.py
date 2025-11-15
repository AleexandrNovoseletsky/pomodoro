"""Зависомости задач."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.database.accesor import get_db_session
from pomodoro.database.cache.accesor import get_cache_session
from pomodoro.task.models.tasks import Task
from pomodoro.task.repositories.cache_tasks import TaskCacheRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.task.services.task_service import TaskService


async def get_task_repository(
    db: Annotated[AsyncSession, Depends(dependency=get_db_session)]
) -> TaskRepository:
    """Получение репозитория задач."""
    return TaskRepository(db_session=db)


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
) -> TaskService:
    """Получение сервиса задач."""
    return TaskService(task_repo=task_repo, cache_repo=cache_repo)


async def get_task_resource(
    task_id: int,
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> Task:
    """Получение одной задачи."""
    return await task_service.get_one_object(object_id=task_id)
