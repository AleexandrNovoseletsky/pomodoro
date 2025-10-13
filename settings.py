from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_PATH: str = (
        'postgresql+psycopg2://' 
        'postgres:password@' # username:password
        '127.0.0.1:5432/pomodoro' # host/database
    )
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
