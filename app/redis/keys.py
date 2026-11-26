# 生成回答缓存的 Redis key
def chat_response_cache_key(question_hash: str) -> str:
    return f"chat:response:{question_hash}"


# 生成限流计数的 Redis key
def rate_limit_key(user_id: str, api_name: str) -> str:
    return f"rate_limit:{api_name}:{user_id}"


# 生成 API Key 缓存的 Redis key
def api_key_cache_key(api_key_hash: str) -> str:
    return f"api_key:{api_key_hash}"


# 生成会话消息缓存的 Redis key
def conversation_recent_messages_key(conversation_id: str) -> str:
    return f"conversation:{conversation_id}:recent_messages"


# 生成 Agent 运行状态的 Redis key
def agent_run_state_key(run_id: str) -> str:
    return f"agent:run:{run_id}:state"


# 生成分布式锁的 Redis key
def lock_key(resource: str, resource_id: str) -> str:
    return f"lock:{resource}:{resource_id}"