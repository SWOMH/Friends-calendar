from redis.asyncio import Redis
from config.constants import DEV_CONSTANT
import os

_url = os.getenv("REDIS_URL")
if _url:
    redis_db = Redis.from_url(_url)
else:
    redis_db = Redis(
        host=DEV_CONSTANT.REDIS_HOST,
        port=DEV_CONSTANT.REDIS_PORT,
        db=DEV_CONSTANT.REDIS_DB,
    )
