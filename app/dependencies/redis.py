from redis.asyncio import Redis
from app.redis.client import redis_client
# 依赖：返回全局 Redis 客户端
async def get_redis_client()->Redis:
    return redis_client