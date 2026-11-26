import json
from typing import Any, Optional

from redis.asyncio import Redis

from app.redis.keys import agent_run_state_key


# 保存 Agent 运行状态到 Redis（默认 1 小时过期）
async def set_agent_run_state(
    redis: Redis,
    run_id: str,
    state: dict[str, Any],
    ttl_seconds: int = 3600,
):
    key = agent_run_state_key(run_id)

    await redis.set(
        key,
        json.dumps(state, ensure_ascii=False),
        ex=ttl_seconds,
    )


# 读取 Agent 运行状态，不存在返回 None
async def get_agent_run_state(
    redis: Redis,
    run_id: str,
) -> Optional[dict[str, Any]]:
    key = agent_run_state_key(run_id)
    value = await redis.get(key)

    if not value:
        return None

    return json.loads(value)