from fastapi import Depends
from sqlalchemy.orm import Session

from database.cache import get_cache_session
from database import get_db_session
from repositories import TaskCacheRepository
from repositories import TaskRepository
from services import TaskService


async def get_task_repository(
        db: Session = Depends(get_db_session)
) -> TaskRepository:
    return TaskRepository(db)


async def get_cache_task_repository() -> TaskCacheRepository | None:
    async for cache_session in get_cache_session():
        return TaskCacheRepository(cache_session)
    return None


async def get_task_service(
        task_repo: TaskRepository = Depends(get_task_repository),
        cache_repo: TaskCacheRepository = Depends(get_cache_task_repository)
) -> TaskService:
    return TaskService(task_repo=task_repo, cache_repo=cache_repo)


async def get_task_resource(
        object_id: int,
        task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_one_object(object_id)
