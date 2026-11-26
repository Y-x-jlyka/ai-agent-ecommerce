from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db_session
from app.dependencies.llm import get_llm_provider
from app.dependencies.rate_limit import chat_rate_limit
from app.dependencies.redis import get_redis_client
from app.llm.base import BaseLLMProvider
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
from app.services.chat_service import chat_with_ai
from app.services.chat_stream_service import stream_chat_with_ai

router = APIRouter()

@router.post(
    "/chat",
    response_model=ApiResponse[ChatResponse],
    dependencies=[Depends(chat_rate_limit)],
)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
) -> ApiResponse[ChatResponse]:
    request.user_id = current_user.user_id

    result = await chat_with_ai(
        request=request,
        db=db,
        redis=redis,
        llm_provider=llm_provider,
    )

    result.trace_id = f"{result.trace_id}_user_{current_user.user_id}"

    return ApiResponse[ChatResponse](
        data=result
    )

@router.post(
    "/chat/stream",
    dependencies=[Depends(chat_rate_limit)],
)
async def chat_stream(
    request_body: ChatRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
):
    request_body.user_id = current_user.user_id
    request_body.stream = True

    async def event_generator():
        async for event in stream_chat_with_ai(
            request=request_body,
            llm_provider=llm_provider,
            db=db,
            redis=redis,
        ):
            if await request.is_disconnected():
                break

            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )