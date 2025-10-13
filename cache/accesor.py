from typing import AsyncGenerator

import redis.asyncio as redis

from settings import Settings


async def get_cache_session() -> AsyncGenerator[redis.Redis, None]:
    cache_session = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    )
    try:
        yield cache_session
    finally:
        await cache_session.aclose()

