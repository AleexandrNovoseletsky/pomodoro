from dependencies.category import (
    get_category_repository, get_category_service
)
from dependencies.task import (
    get_cache_task_repository,
    get_task_repository,
    get_task_resource,
    get_task_service
)
from dependencies.user import (
    get_current_user, get_user_repository, get_user_service
)

__all__ = [
    'get_current_user',
    'get_user_repository',
    'get_user_service',
    'get_cache_task_repository',
    'get_task_repository',
    'get_task_service',
    'get_category_repository',
    'get_task_resource',
    'get_category_service',
]
