from unittest import result

from fastapi import APIRouter,Depends
from app.core.config import Settings
from app.dependencies.settings import get_app_settings
from fastapi import Depends
from redis.asyncio import Redis

from app.dependencies.redis import get_redis_client

router=APIRouter()

@router.get("/system-error-demo")
# 演示未捕获异常：故意除零，用于触发全局异常处理器
async def system_error_demo():
    result=1/0
    return {"result":result}




@router.get("/health")
# 健康检查：返回服务名称、环境和版本
async def health(
        settings:Settings=Depends(get_app_settings)):
    return {"status":"ok","service":settings.app_name,
            "env":settings.app_env,
            "version":settings.app_version,
            }
@router.get("/health/redis")
# Redis 健康检查：ping 通返回 ok
async def redis_health(
    redis: Redis = Depends(get_redis_client),
):
    pong = await redis.ping()

    return {
        "status": "ok" if pong else "error",
        "redis": pong,
    }