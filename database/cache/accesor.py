from typing import AsyncGenerator

import redis.asyncio as redis

from settings import Settings

settings = Settings()


async def get_cache_session() -> AsyncGenerator[redis.Redis, None]:
    cache_session = redis.Redis(
        host=settings.CACHE_HOST,
        port=settings.CACHE_PORT,
        db=settings.CACHE_DB_NAME,
        decode_responses=True,
    )
    try:
        yield cache_session
    finally:
        await cache_session.aclose()
