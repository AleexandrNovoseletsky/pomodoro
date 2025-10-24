from fastapi import Depends

from cache import get_cache_session
from database import get_db_session
from repositories import CategoryRepository
from repositories import TaskRepository
from repositories import TaskCacheRepository
from services import CategoryService
from services import TaskService


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

async def get_category_service(
        category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    return CategoryService(category_repo)
