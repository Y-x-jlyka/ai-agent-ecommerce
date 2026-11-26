import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


# 关闭全局 Redis 连接
async def close_redis():
    await redis_client.aclose()