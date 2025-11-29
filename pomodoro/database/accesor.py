"""Utilities for accessing the database (SQLAlchemy).

Exports the `get_db_session` session factory for use as a FastAPI
dependency.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pomodoro.core.settings import Settings

settings = Settings()

# Async engine and session factory for SQLAlchemy AsyncIO
engine: AsyncEngine = create_async_engine(settings.ASYNC_DB_PATH, echo=False)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
