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
    DB_DRIVER: str = 'postgresql+psycopg2'

    @property
    def db_url(self) -> str:
        return (
        f'{self.DB_DRIVER}://' # driver://
        f'{self.DB_USERNAME}:{self.DB_PASSWORD}@' # username:password
        f'{self.DB_HOST}:{int(self.DB_PORT)}/' # host:port/
        f'{self.DB_NAME}' # database
    )

    CACHE_HOST: str = os.getenv('CACHE_HOST')
    CACHE_PORT: int = os.getenv('CACHE_PORT')
    CACHE_DB_NAME: int = os.getenv('CACHE_DB_NAME')
    CACHE_LIFESPAN: int = 60 # in seconds
