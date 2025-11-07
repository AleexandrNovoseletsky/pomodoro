import json

from redis.asyncio import Redis

from schemas.task import ResponseTaskSchema
from settings import Settings

settings = Settings()


class TaskCacheRepository:

    def __init__(self, cache_session: Redis) -> None:
        self.cache_session = cache_session

    async def get_all_tasks(
        self, key: str = "all_tasks"
    ) -> list[ResponseTaskSchema] | None:
        tasks_json = await self.cache_session.get(name=key)
        if tasks_json is None:
            return None
        return [
            ResponseTaskSchema.model_validate(task)
            for task in json.loads(s=tasks_json)
        ]

    async def set_all_tasks(
        self, tasks: list[ResponseTaskSchema], key: str = "all_tasks"
    ) -> None:
        tasks_json = json.dumps(
            [task.model_dump() for task in tasks],
            ensure_ascii=False,
            default=str,
        )
        await self.cache_session.set(
            name=key, value=tasks_json, ex=settings.CACHE_LIFESPAN
        )
