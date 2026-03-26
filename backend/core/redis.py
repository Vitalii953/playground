import redis.asyncio as redis
from redis.asyncio import Redis
from backend.core.config import get_settings


settings = get_settings()


async def get_redis() -> Redis:
    redis_client = redis.from_url(
        str(settings.redis_url), encoding="utf-8", decode_responses=True
    )
    return redis_client
