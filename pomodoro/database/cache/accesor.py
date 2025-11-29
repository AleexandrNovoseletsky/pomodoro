"""Asynchronous access to Redis (using redis.asyncio).

Exports the dependency `get_cache_session` for use in FastAPI
dependencies.
"""

from collections.abc import AsyncGenerator

import redis.asyncio as redis

from pomodoro.core.settings import Settings

settings = Settings()


def create_redis_connection() -> redis.Redis:
    """Create a connection to Redis."""
    return redis.Redis(
        host=settings.CACHE_HOST,
        port=settings.CACHE_PORT,
        db=settings.CACHE_DB_NAME,
        decode_responses=True,
    )


async def get_cache_session() -> AsyncGenerator[redis.Redis, None]:
    """Return the Redis connection and close it correctly in finally.

    The Redis client is created on each call.
    """
    cache_session = create_redis_connection()
    try:
        yield cache_session
    finally:
        await cache_session.aclose()
