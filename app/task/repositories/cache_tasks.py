"""Репозиторий для кэширования задач."""
import json

from redis.asyncio import Redis

from app.core.settings import Settings
from app.task.schemas.task import ResponseTaskSchema

settings = Settings()


class TaskCacheRepository:
    """Репозиторий для кэширования задач."""

    def __init__(self, cache_session: Redis) -> None:
        """Инициализирует репозиторий сессией Redis."""
        self.cache_session = cache_session

    async def get_all_tasks(
        self, key: str = "all_tasks"
    ) -> list[ResponseTaskSchema] | None:
        """Получаем все задачи из кэша, если есть."""
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
        """Сохраняем все задачи в кэш."""
        tasks_json = json.dumps(
            [task.model_dump() for task in tasks],
            ensure_ascii=False,
            default=str,
        )
        await self.cache_session.set(
            name=key, value=tasks_json, ex=settings.CACHE_LIFESPAN
        )
