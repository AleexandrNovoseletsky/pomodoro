import os
from datetime import timedelta

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DEV: bool = True
PROD: bool = not DEV

if DEV:
    load_dotenv('.dev_env')
elif PROD:
    load_dotenv('.env')


class Settings(BaseSettings):
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_USERNAME: str = os.getenv('DB_USERNAME')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')

    DB_PATH: str = (
        'postgresql+psycopg2://' 
        f'{DB_USERNAME}:{DB_PASSWORD}@' # username:password
        f'{DB_HOST}:{int(DB_PORT)}/{DB_NAME}' # host/database
    )

    CACHE_HOST: str = os.getenv('CACHE_HOST')
    CACHE_PORT: int = os.getenv('CACHE_PORT')
    CACHE_DB_NAME: int = os.getenv('CACHE_DB_NAME')
    CACHE_LIFESPAN: int = 600 # in seconds

    MIN_LOGIN_LENGTH: int = 2
    MAX_LOGIN_LENGTH: int = 30
    MIN_USER_NAME_LENGTH: int = 2
    MAX_USER_NAME_LENGTH: int = 30
    MAX_USER_ABOUT_LENGTH: int = 5000
    MIN_PASSWORD_LENGTH: int = 8
    MAX_EMAIL_LENGTH: int = 255

    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    JWT_LIFE_SPAN: timedelta = timedelta(weeks=4)
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM')

    CRYPTO_CONTEXT: str = os.getenv('CRYPTO_CONTEXT')

    MIN_CATEGORY_NAME_LENGTH: int = 1
    MAX_CATEGORY_NAME_LENGTH: int = 30

    MIN_TASK_NAME_LENGTH: int = 1
    MAX_TASK_NAME_LENGTH: int = 30

    MIN_POMODORO_COUNT: int = 1
    MAX_POMODORO_COUNT: int = 1000
