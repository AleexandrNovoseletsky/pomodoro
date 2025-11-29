"""ASGI application entry point for local import in uvicorn.

Routes are explicitly connected, and custom exception handlers are
registered globally.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from pomodoro.auth.handlers.auth import router as auth_router
from pomodoro.core.exceptions.base import AppException
from pomodoro.core.handlers.exceptions_handlers import app_exception_handler
from pomodoro.database.cache.accesor import (
    create_redis_connection,
)
from pomodoro.media.handlers.media import router as media_router
from pomodoro.task.handlers.categories import router as category_router
from pomodoro.task.handlers.tasks import router as task_router
from pomodoro.user.handlers.users import router as user_router

# Configure basic logging at INFO level so all module-level
# `logger.info(...)` messages (including timing marks [TIMING])
# are output to stdout/stderr and included in log files during redirection.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan manager for startup and shutdown events.

    Handles: - Redis connection initialization for rate limiting -
    FastAPILimiter setup - Proper resource cleanup during shutdown

    Args:     application: FastAPI application instance
    """
    # Use function from database layer for consistent Redis configuration
    redis_connection = create_redis_connection()
    await FastAPILimiter.init(redis_connection)
    logging.info("✅ Rate limiter initialized with Redis")

    # Application runs during this yield
    yield

    # Clean shutdown procedures
    await FastAPILimiter.close()
    await redis_connection.aclose()
    logging.info("✅ Rate limiter closed")


app = FastAPI(
    title="Pomodoro API",
    description=("Pomodoro technique task management API "
                 "with user authentication and media support"),
    version="1.0.0",
    lifespan=lifespan,
)

# Register custom application exception handler globally
app.add_exception_handler(AppException, app_exception_handler)

# Connect routers. Prefixes are specified here
# (handlers don't specify prefixes)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(media_router, prefix="/media", tags=["Media Management"])
app.include_router(task_router, prefix="/tasks", tags=["Task Management"])
app.include_router(
    category_router, prefix="/categories", tags=["Category Management"]
)
app.include_router(user_router, prefix="/users", tags=["User Management"])
