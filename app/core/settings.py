import os
from datetime import timedelta

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DEV: bool = True
PROD: bool = not DEV

if DEV:
    load_dotenv(".dev_env")
elif PROD:
    load_dotenv(".env")


class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", default="localhost")
    DB_PORT: str = os.getenv("DB_PORT", default="5432")
    DB_NAME: str = os.getenv("DB_NAME", default="pomodoro_db")
    DB_USERNAME: str = os.getenv("DB_USERNAME", default="user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", default="password")
    DB_DRIVER: str = "postgresql+psycopg2://"
    # Async driver for SQLAlchemy (requires asyncpg in dependencies)
    ASYNC_DB_DRIVER: str = "postgresql+asyncpg://"

    DB_PATH: str = (
        f"{DB_DRIVER}"
        f"{DB_USERNAME}:{DB_PASSWORD}@"  # username:password
        f"{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"  # host/database
    )

    ASYNC_DB_PATH: str = (
        f"{ASYNC_DB_DRIVER}"
        f"{DB_USERNAME}:{DB_PASSWORD}@"
        f"{DB_HOST}:{int(DB_PORT)}/{DB_NAME}"
    )

    CACHE_HOST: str = os.getenv("CACHE_HOST", default="localhost")
    CACHE_PORT: int = int(os.getenv("CACHE_PORT", default=6379))
    CACHE_DB_NAME: int = int(os.getenv("CACHE_DB_NAME", default=0))
    CACHE_LIFESPAN: int = 600  # in seconds

    MIN_LOGIN_LENGTH: int = 2
    MAX_LOGIN_LENGTH: int = 30
    MIN_USER_NAME_LENGTH: int = 2
    MAX_USER_NAME_LENGTH: int = 30
    MAX_USER_ABOUT_LENGTH: int = 5000
    MIN_PASSWORD_LENGTH: int = 8
    MAX_EMAIL_LENGTH: int = 255

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", default="secretkey")
    JWT_LIFE_SPAN: timedelta = timedelta(weeks=4)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", default="HS256")

    CRYPTO_CONTEXT: str = os.getenv("CRYPTO_CONTEXT", default="argon2")

    MIN_CATEGORY_NAME_LENGTH: int = 1
    MAX_CATEGORY_NAME_LENGTH: int = 30

    MIN_TASK_NAME_LENGTH: int = 1
    MAX_TASK_NAME_LENGTH: int = 30

    MIN_POMODORO_COUNT: int = 1
    MAX_POMODORO_COUNT: int = 1000

    YANDEX_CLIENT_ID: str = os.getenv(
        "YANDEX_CLIENT_ID", default="YANDEX_CLIENT_ID"
        )
    YANDEX_CLIENT_SECRET: str = os.getenv(
        "YANDEX_CLIENT_SECRET", default="YANDEX_CLIENT_SECRET"
        )
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/auth/yandex"

    @property
    def get_yandex_redirect_url(self) -> str:
        return ("https://oauth.yandex.ru/authorize?response_type=code"
                f"&client_id={self.YANDEX_CLIENT_ID}"
                f"&redirect_uri={self.YANDEX_REDIRECT_URI}"
                )
