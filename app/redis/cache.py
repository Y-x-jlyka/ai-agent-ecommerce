import json
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings
from app.redis.keys import conversation_recent_messages_key
from app.schemas.chat import ChatMessage, MessageRole
import hashlib
from app.redis.keys import chat_response_cache_key
import hashlib

from app.redis.keys import chat_response_cache_key
import uuid

from redis.asyncio import Redis

from app.redis.keys import lock_key

from app.redis.keys import api_key_cache_key

# 缓存会话最近的消息列表
async def cache_recent_messages(
    redis: Redis,
    conversation_id: str,
    messages: list[ChatMessage],
    ttl_seconds: Optional[int] = None,
):
    key = conversation_recent_messages_key(conversation_id)

    data = [
        {
            "role": message.role.value,
            "content": message.content,
        }
        for message in messages
    ]

    await redis.set(
        key,
        json.dumps(data, ensure_ascii=False),
        ex=ttl_seconds or settings.redis_default_ttl_seconds,
    )


# 读取缓存的消息列表
async def get_cached_recent_messages(
    redis: Redis,
    conversation_id: str,
) -> Optional[list[ChatMessage]]:
    key = conversation_recent_messages_key(conversation_id)
    value = await redis.get(key)

    if not value:
        return None

    data = json.loads(value)

    return [
        ChatMessage(
            role=MessageRole(item["role"]),
            content=item["content"],
        )
        for item in data
    ]



# 对文本做 SHA256 哈希，用于构造缓存 key
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# 按问题读取缓存的回答
async def get_cached_chat_response(
    redis: Redis,
    question: str,
) -> Optional[str]:
    key = chat_response_cache_key(hash_text(question))
    return await redis.get(key)


# 按问题缓存回答（默认 5 分钟）
async def cache_chat_response(
    redis: Redis,
    question: str,
    answer: str,
    ttl_seconds: int = 300,
):
    key = chat_response_cache_key(hash_text(question))

    await redis.set(
        key,
        answer,
        ex=ttl_seconds,
    )


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



# 缓存 API Key 对应的用户 ID
async def cache_api_key_user(
    redis: Redis,
    api_key_hash: str,
    user_id: str,
    ttl_seconds: int = 600,
):
    key = api_key_cache_key(api_key_hash)

    await redis.set(
        key,
        user_id,
        ex=ttl_seconds,
    )


# 读取 API Key 对应的用户 ID
async def get_cached_api_key_user(
    redis: Redis,
    api_key_hash: str,
) -> Optional[str]:
    key = api_key_cache_key(api_key_hash)

    return await redis.get(key)