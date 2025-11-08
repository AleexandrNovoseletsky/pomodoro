"""Асинхронный доступ к Redis (используется redis.asyncio).

Экспортирует dependency `get_cache_session` для использования в
FastAPI-зависимостях.
"""

from typing import AsyncGenerator

import redis.asyncio as redis

from app.core.settings import Settings

settings = Settings()


async def get_cache_session() -> AsyncGenerator[redis.Redis, None]:
    """Вернуть подключение к Redis и корректно закрыть его в finally.

    Redis клиент создаётся на каждом вызове — это простой и безопасный
    подход для сервисов с небольшим трафиком. Для оптимизации можно
    реиспользовать клиент на уровне приложения.
    """
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
