from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user
from app.langchain_tools.registry import langchain_tool_registry
from app.langchain_tools.service import langchain_tool_calling_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser

router = APIRouter()#LangChain 工具路由：查询工具清单 + 走 LangChain 链路的客服对话

class LangChainToolChatRequest(BaseModel):#LangChain 工具对话请求体：问题 + 供应商与模型
    question: str = Field(..., min_length=1, description="用户问题")
    provider: str = Field(default="deepseek", description="模型供应商")
    model: str = Field(default="deepseek-chat", description="模型名称")

@router.get(
    "/langchain/tools",
    response_model=ApiResponse[list[dict]],
)
# 工具清单接口：返回全部已注册 LangChain 工具的名称、描述与参数结构
async def list_langchain_tools(
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[list[dict]]:
    # 注意：方法名是 list_tools（不能用 list，会遮蔽内置类型）
    tools = langchain_tool_registry.list_tools()

    return ApiResponse[list[dict]](
        data=[
            {
                "name": item.name,
                "description": item.description,
                "args": item.args,
            }
            for item in tools
        ]
    )

@router.post(
    "/langchain/tools/chat",
    response_model=ApiResponse[dict],
)
# 工具对话接口：让模型自主决定是否调用工具，基于执行结果生成回答
async def langchain_tool_chat(
    request: LangChainToolChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ApiResponse[dict]:
    result = await langchain_tool_calling_service.run_ecommerce_customer_service(
        user_question=request.question,
        provider=request.provider,
        model_name=request.model,
    )

    return ApiResponse[dict](
        data=result
    )
