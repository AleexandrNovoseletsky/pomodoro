"""Настройки приложения Pomodoro."""

import os
from datetime import timedelta

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Определяем окружение
DEV: bool = True
PROD: bool = not DEV

if DEV:
    load_dotenv(".dev_env")
elif PROD:
    load_dotenv(".env")


class Settings(BaseSettings):
    """Основные настройки приложения Pomodoro.

    Включает параметры БД, кеша, JWT, валидацию пользователей и задач,
    а также интеграцию с Яндекс OAuth.
    """

    # --- Database ---
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "pomodoro_db")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_DRIVER: str = "postgresql+psycopg2://"
    ASYNC_DB_DRIVER: str = "postgresql+asyncpg://"

    DB_PATH: str = (
        f"{DB_DRIVER}{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )
    ASYNC_DB_PATH: str = (
        f"{ASYNC_DB_DRIVER}{DB_USERNAME}:{DB_PASSWORD}"
        f"@{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )

    # --- Cache / Redis ---
    CACHE_HOST: str = os.getenv("CACHE_HOST", default="localhost")
    CACHE_PORT: int = int(os.getenv("CACHE_PORT", default=6379))
    CACHE_DB_NAME: int = int(os.getenv("CACHE_DB_NAME", default=0))
    CACHE_LIFESPAN: int = 600  # seconds

    # --- User validation ---
    MIN_LOGIN_LENGTH: int = 2
    MAX_LOGIN_LENGTH: int = 30
    MIN_USER_NAME_LENGTH: int = 2
    MAX_USER_NAME_LENGTH: int = 30
    MAX_USER_ABOUT_LENGTH: int = 5000
    MIN_PASSWORD_LENGTH: int = 8
    MAX_EMAIL_LENGTH: int = 255

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", default="secretkey")
    JWT_LIFE_SPAN: timedelta = timedelta(weeks=4)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", default="HS256")

    # --- Password hashing ---
    CRYPTO_CONTEXT: str = os.getenv("CRYPTO_CONTEXT", default="argon2")

    # --- Categories ---
    MIN_CATEGORY_NAME_LENGTH: int = 1
    MAX_CATEGORY_NAME_LENGTH: int = 30

    # --- Tasks ---
    MIN_TASK_NAME_LENGTH: int = 1
    MAX_TASK_NAME_LENGTH: int = 30
    MIN_POMODORO_COUNT: int = 1
    MAX_POMODORO_COUNT: int = 1000

    # --- Yandex OAuth ---
    YANDEX_CLIENT_ID: str = os.getenv(
        "YANDEX_CLIENT_ID", default="YANDEX_CLIENT_ID"
        )
    YANDEX_CLIENT_SECRET: str = os.getenv(
        "YANDEX_CLIENT_SECRET", default="YANDEX_CLIENT_SECRET"
        )
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/auth/yandex"

    @property
    def get_yandex_redirect_url(self) -> str:
        """URL для авторизации через Яндекс."""
        return (
            f"https://oauth.yandex.ru/authorize?response_type=code"
            f"&client_id={self.YANDEX_CLIENT_ID}"
            f"&redirect_uri={self.YANDEX_REDIRECT_URI}"
        )
