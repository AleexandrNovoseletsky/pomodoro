from fastapi.params import Depends

from cache.accesor import get_cache_session
from database import get_db_session
from repository.category import CategoryRepository
from repository.task import TaskRepository
from repository.cache_tasks import TaskCacheRepository


async def get_task_repository() -> TaskRepository:
    db_session = get_db_session()
    return TaskRepository(db_session)

async def get_cache_task_repository(
        cache_session = Depends(get_cache_session)
) -> TaskCacheRepository:
    return TaskCacheRepository(cache_session)

async def get_category_repository() -> CategoryRepository:
    db_session = get_db_session()
    return CategoryRepository(db_session)
