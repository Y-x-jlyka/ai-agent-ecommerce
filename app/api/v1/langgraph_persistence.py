from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langgraph_persistence.service import langgraph_persistence_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser


router = APIRouter()


class PersistenceChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)
    tenant_id: str = Field(default="tenant_001")


@router.post(
    "/langgraph/persistence/chat",
    response_model=ApiResponse[dict],
)
async def persistence_chat(
    request: PersistenceChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_persistence_service.continue_flow(
        user_question=request.question,
        tenant_id=request.tenant_id,
        user_id=current_user.user_id,
        conversation_id=request.conversation_id,
    )

    # 图可能提前结束（如缺订单号走 ask_order_id 路径），
    # 此时 order_status / policy_answer 等字段从未被写入，不在 state 里，
    # 必须用 .get() 防御式读取，硬取键会 KeyError
    return ApiResponse[dict](
        data={
            "answer": result.get("final_answer", ""),
            "intent": result.get("intent", "unknown"),
            "order_id": result.get("order_id"),
            "order_status": result.get("order_status"),
            "need_user_input": result.get("need_user_input", False),
            "waiting_for": result.get("waiting_for"),
            "logs": result.get("logs", []),
        }
    )


@router.get(
    "/langgraph/persistence/state/{conversation_id}",
    response_model=ApiResponse[dict],
)
async def get_persistence_state(
    conversation_id: str,
    tenant_id: str = "tenant_001",
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = langgraph_persistence_service.get_current_state(
        tenant_id=tenant_id,
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return ApiResponse[dict](
        data=result
    )