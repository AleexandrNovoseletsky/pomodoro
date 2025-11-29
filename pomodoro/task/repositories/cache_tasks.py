"""Task cache repository.

Provides Redis-based caching layer for task data to improve performance
and reduce database load for frequently accessed task information.
"""

import json

from redis.asyncio import Redis

from pomodoro.core.settings import Settings
from pomodoro.task.schemas.task import ResponseTaskSchema

settings = Settings()


class TaskCacheRepository:
    """Redis cache repository for task data operations.

    Handles caching and retrieval of task data to optimize performance
    and reduce database queries for frequently accessed task
    information.

    Attributes:     cache_session: Redis client instance for cache
    operations
    """

    def __init__(self, cache_session: Redis) -> None:
        """Initialize repository with Redis cache session.

        Args:     cache_session: Authenticated Redis client for cache
        operations
        """
        self.cache_session = cache_session

    async def get_all_tasks(
        self, key: str = "all_tasks"
    ) -> list[ResponseTaskSchema] | None:
        """Retrieve all tasks from cache if available.

        Args:     key: Cache key for tasks data (default: "all_tasks")

        Returns:     List of validated task schemas if cache hit, None
        if cache miss

        Note:     Returns None if data is not found in cache or cache is
        unavailable
        """
        tasks_json = await self.cache_session.get(name=key)
        if tasks_json is None:
            return None
        return [
            ResponseTaskSchema.model_validate(task)
            for task in json.loads(tasks_json)
        ]

    async def set_all_tasks(
        self, tasks: list[ResponseTaskSchema], key: str = "all_tasks"
    ) -> None:
        """Store all tasks in cache with configurable expiration.

        Args:     tasks: List of task schemas to cache     key: Cache
        key for tasks data (default: "all_tasks")

        Note:     Uses application settings for cache lifespan
        configuration     Ensures proper JSON serialization with Unicode
        support
        """
        tasks_json = json.dumps(
            [task.model_dump() for task in tasks],
            ensure_ascii=False,
            default=str,
        )
        await self.cache_session.set(
            name=key, value=tasks_json, ex=settings.CACHE_LIFESPAN
        )
