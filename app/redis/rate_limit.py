from redis.asyncio import Redis

from app.core.config import settings
from app.redis.keys import rate_limit_key


# 计数判断是否允许访问，返回是否放行与剩余时间
async def check_rate_limit(redis: Redis, user_id: str, api_name: str) -> tuple[bool, int, int]:
    key = rate_limit_key(user_id=user_id, api_name=api_name)
    current = await redis.incr(key)



    if current == 1:
        await redis.expire(key, settings.rate_limit_window_seconds)
    ttl = await redis.ttl(key)
    allowed = current <= settings.rate_limit_max_requests
    return allowed, current, ttl