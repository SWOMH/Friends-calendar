from pydantic_settings import BaseSettings
from typing import Optional


class Constants(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    AUTH_DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"


    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"


DEV_CONSTANT = Constants()