"""Точка входа ASGI-приложения для локального импорта в uvicorn.

Роуты подключаются явным образом, а обработчик пользовательских
исключений регистрируется глобально.
"""

import logging

from fastapi import FastAPI

from pomodoro.auth.handlers.auth import router as auth_router
from pomodoro.core.exceptions.base import AppException
from pomodoro.core.handlers.exceptions_handlers import app_exception_handler
from pomodoro.media.handlers.media import router as media_router
from pomodoro.task.handlers.categories import router as category_router
from pomodoro.task.handlers.tasks import router as task_router
from pomodoro.user.handlers.users import router as user_router

# Настроим базовое логирование на уровне INFO, чтобы все модульные
# `logger.info(...)` сообщения (включая временные метки [TIMING])
# выводились в stdout/stderr и попадали в лог-файл при редиректе.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
)

app = FastAPI()

# Регистрируем обработчик кастомных исключений приложения
app.add_exception_handler(AppException, app_exception_handler)

# Подключаем роутеры. Префиксы задаются здесь (handlers не указывают префиксы)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(media_router, prefix="/media", tags=["Media"])
app.include_router(task_router, prefix="/tasks", tags=["tasks"])
app.include_router(category_router, prefix="/categories", tags=["categories"])
app.include_router(user_router, prefix="/users", tags=["users"])
