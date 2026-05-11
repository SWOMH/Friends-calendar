from pydantic_settings import BaseSettings
from typing import Optional


class Constants(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    SECRET_KEY: str = "demo-seckret-key-not-prod"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 40
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"


DEV_CONSTANT = Constants()