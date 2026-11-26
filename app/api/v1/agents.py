

from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field
from redis.asyncio import Redis
from app.dependencies.redis import get_redis_client
from app.redis.agent_state import (get_agent_run_state,set_agent_run_state)
import uuid


from app.dependencies.agent_context import AgentContext,get_agent_context
from app.schemas.response import ApiResponse

router=APIRouter()#当前模块的路由对象，注册后由 api_router 统一挂载到 /api/v1 下

class AgentRunRequest(BaseModel):#Agent 运行请求体：一次 Agent 调用需要传入的入参
    question:str=Field(...,min_length=1,description="用户问题")
    agent_id:str=Field(default="agent_chat",description="Agent ID")
class AgentRunResponse(BaseModel):#Agent 运行响应体：同步调用返回的结果
    answer:str=Field(...,description="Agent回答")
    trace_id:str=Field(...,description="链路追踪 ID")
    debug:bool=Field(default=False,description="是否调试模式")

@router.post("/agent/run",response_model=ApiResponse[dict])
# 同步执行 Agent：处理完成后一次性返回结果，适合短任务
async def run_agent(
        request:AgentRunRequest,
        context:AgentContext=Depends(get_agent_context)
)->ApiResponse[AgentRunResponse]:
    answer=(
        f"用户{context.current_user.username}调用了{request.agent_id},"
        f"问题是{request.question}"
            )
    return ApiResponse[AgentRunResponse](
        data=AgentRunResponse(
            answer=answer,
            trace_id=context.trace_id,
            debug=context.debug))
@router.post("/agents/run-async", response_model=ApiResponse[dict])
# 异步执行 Agent：只登记任务状态到 Redis 并立即返回 run_id，客户端需轮询查询结果
async def run_agent_async(
    request: AgentRunRequest,
    redis: Redis = Depends(get_redis_client),
    context: AgentContext = Depends(get_agent_context),
) -> ApiResponse[dict]:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    await set_agent_run_state(
        redis=redis,
        run_id=run_id,
        state={
            "run_id": run_id,
            "agent_id": request.agent_id,
            "question": request.question,
            "status": "running",
            "current_step": "planning",
            "progress": 10,
            "trace_id": context.trace_id,
        },
    )

    return ApiResponse[dict](
        data={
            "run_id": run_id,
            "status": "running",
            "trace_id": context.trace_id,
        }
    )


@router.get("/agents/runs/{run_id}", response_model=ApiResponse[dict])
# 查询 Agent 运行状态：配合 /agents/run-async 使用，用 run_id 轮询进度
async def get_agent_run(
    run_id: str,
    redis: Redis = Depends(get_redis_client),
) -> ApiResponse[dict]:
    state = await get_agent_run_state(
        redis=redis,
        run_id=run_id,
    )

    if not state:
        return ApiResponse[dict](
            code=40400,
            message="Agent Run 不存在或已过期",
            data=None,
        )

    return ApiResponse[dict](
        data=state
    )