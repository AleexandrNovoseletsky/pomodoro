"""Утилиты для доступа к базе данных (SQLAlchemy).

Экспортирует фабрику сессий `get_db_session` для использования как
FastAPI-зависимость.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pomodoro.core.settings import Settings

settings = Settings()

# Асинхронный движок и фабрика сессий для SQLAlchemy AsyncIO
engine: AsyncEngine = create_async_engine(settings.ASYNC_DB_PATH, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор сессии.

    Пример:
        db: AsyncSession = Depends(get_db_session)
    """
    async with AsyncSessionLocal() as session:
        yield session
