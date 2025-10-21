from dotenv import load_dotenv
import os

from pydantic_settings import BaseSettings

DEV: bool = True
PROD: bool = not DEV

if DEV is True:
    load_dotenv('.dev_env')
elif PROD is True:
    load_dotenv('.prod_env')


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
