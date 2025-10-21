from fastapi import Depends
from cache.accesor import get_cache_session
from database import get_db_session
from repository.category import CategoryRepository
from repository.task import TaskRepository
from repository.cache_tasks import TaskCacheRepository
from services.task_service import TaskService


async def get_task_repository() -> TaskRepository:
    db_session = get_db_session()
    return TaskRepository(db_session)

async def get_cache_task_repository() -> TaskCacheRepository | None:
    async for cache_session in get_cache_session():
        return TaskCacheRepository(cache_session)
    return None

async def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    cache_repo: TaskCacheRepository = Depends(get_cache_task_repository)
) -> TaskService:
    return TaskService(task_repo, cache_repo)

async def get_category_repository() -> CategoryRepository:
    db_session = get_db_session()
    return CategoryRepository(db_session)
