import uuid
from typing import Optional

from redis.asyncio import Redis

from app.redis.keys import lock_key


# 获取分布式锁（nx 保证互斥，返回令牌）
async def acquire_lock(
    redis: Redis,
    resource: str,
    resource_id: str,
    ttl_seconds: int = 30,
) -> Optional[str]:
    key = lock_key(resource, resource_id)
    token = str(uuid.uuid4())

    success = await redis.set(
        key,
        token,
        ex=ttl_seconds,
        nx=True,
    )

    if success:
        return token

    return None


# 释放分布式锁（校验令牌一致才删除）
async def release_lock(
    redis: Redis,
    resource: str,
    resource_id: str,
    token: str,
) -> bool:
    key = lock_key(resource, resource_id)

    current_token = await redis.get(key)

    if current_token != token:
        return False

    await redis.delete(key)
    return True