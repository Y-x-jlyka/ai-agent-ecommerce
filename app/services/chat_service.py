import uuid
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import LLMProviderError
from app.llm.factory import LLMProviderFactory
from app.llm.schemas import LLMMessage, LLMRequest, LLMRole
from app.prompts.base import PromptScenario
from app.redis.cache import cache_chat_response, get_cached_chat_response
from app.repositories.conversation_repository import conversation_repository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    MessageRole,
    SourceDocument,
    TokenUsage,
)
from app.services.prompt_service import prompt_service
from app.services.tool_calling_service import tool_calling_service

logger = get_logger(__name__)

# 对话主流程：查缓存 → 渲染提示词 → 调大模型 → 写缓存 → 落库 → 返回响应
async def chat_with_ai(
    request: ChatRequest,
    db: Optional[AsyncSession] = None,
    redis: Optional[Redis] = None,
    llm_provider: Optional[BaseLLMProvider] = None,
) -> ChatResponse:
    latest_user_message = get_latest_user_message(request)
    model = request.model or settings.default_model

    logger.info(
        f"chat_start model={model} "
        f"session_id={request.session_id} "
        f"scenario={request.prompt_scenario}"
    )

    if should_use_tool_calling(request):
        return await chat_with_tools(
            request=request,
            latest_user_message=latest_user_message,
            model=model,
            llm_provider=llm_provider,
            db=db,
            redis=redis,
        )

    if redis:
        cached_answer = await get_cached_chat_response(
            redis=redis,
            question=latest_user_message,
        )

        if cached_answer:
            logger.info("chat_response_cache_hit")

            return ChatResponse(
                answer=cached_answer,
                model=model,
                session_id=request.session_id,
                message_id=f"m_{uuid.uuid4().hex[:8]}",
                usage=TokenUsage(),
                sources=[],
                trace_id=f"trace_{uuid.uuid4().hex[:8]}",
                metadata={
                    "cache_hit": True,
                },
            )

    llm_provider = llm_provider or LLMProviderFactory.create()

    llm_request = build_llm_request_from_chat_request(
        request=request,
        model=model,
    )

    try:
        llm_response = await llm_provider.chat(llm_request)

    except LLMProviderError as exc:
        logger.exception(
            f"chat_llm_provider_error provider={exc.provider} "
            f"status_code={exc.status_code}"
        )

        raise AppException(
            message=exc.message,
            code=ErrorCode.LLM_CALL_FAILED,
            status_code=500,
            data={
                "provider": exc.provider,
                "status_code": exc.status_code,
            },
        ) from exc

    answer = llm_response.content

    usage = TokenUsage(
        prompt_tokens=llm_response.usage.prompt_tokens,
        completion_tokens=llm_response.usage.completion_tokens,
        total_tokens=llm_response.usage.total_tokens,
    )

    if redis and answer:
        await cache_chat_response(
            redis=redis,
            question=latest_user_message,
            answer=answer,
        )

    if db and request.session_id:
        await save_chat_messages(
            db=db,
            conversation_id=request.session_id,
            user_message=latest_user_message,
            assistant_message=answer,
            model=model,
            usage=usage,
        )

    logger.info(
        f"chat_success model={model} "
        f"answer_length={len(answer)} "
        f"total_tokens={usage.total_tokens}"
    )

    return ChatResponse(
        answer=answer,
        model=model,
        session_id=request.session_id or f"s_{uuid.uuid4().hex[:8]}",
        message_id=f"m_{uuid.uuid4().hex[:8]}",
        usage=usage,
        sources=build_mock_sources(latest_user_message),
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
        metadata={
            "cache_hit": False,
        },
    )

# 判断是否走工具调用链路：当前只有电商客服场景启用
def should_use_tool_calling(request: ChatRequest) -> bool:
    return request.prompt_scenario == PromptScenario.ECOMMERCE_CUSTOMER_SERVICE.value

# 带工具调用的对话：让模型先决定调哪个工具，再基于执行结果生成最终回答
async def chat_with_tools(
    request: ChatRequest,
    latest_user_message: str,
    model: str,
    llm_provider: Optional[BaseLLMProvider],
    db: Optional[AsyncSession] = None,
    redis: Optional[Redis] = None,
) -> ChatResponse:
    llm_provider = llm_provider or LLMProviderFactory.create()

    tool_result = await tool_calling_service.run_with_tools(
        user_question=latest_user_message,
        model=model,
        llm_provider=llm_provider,
    )

    answer = tool_result["answer"]
    usage = build_usage_from_tool_result(tool_result)

    if redis and answer:
        await cache_chat_response(
            redis=redis,
            question=latest_user_message,
            answer=answer,
        )

    if db and request.session_id:
        await save_chat_messages(
            db=db,
            conversation_id=request.session_id,
            user_message=latest_user_message,
            assistant_message=answer,
            model=model,
            usage=usage,
        )

    return ChatResponse(
        answer=answer,
        model=model,
        session_id=request.session_id or f"s_{uuid.uuid4().hex[:8]}",
        message_id=f"m_{uuid.uuid4().hex[:8]}",
        usage=usage,
        sources=[],
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
        metadata={
            "tool_calls": tool_result.get("tool_calls", []),
            "tool_results": tool_result.get("tool_results", []),
        },
    )

# 汇总工具调用的 token 用量：调过工具时把首次与最终两次调用的用量相加
def build_usage_from_tool_result(tool_result: dict) -> TokenUsage:
    usage_data = tool_result.get("usage") or {}

    if {"first", "final"} <= set(usage_data):
        parts = [usage_data["first"], usage_data["final"]]
    else:
        parts = [usage_data]

    usage = TokenUsage()

    for part in parts:
        usage.prompt_tokens += part.get("prompt_tokens", 0)
        usage.completion_tokens += part.get("completion_tokens", 0)
        usage.total_tokens += part.get("total_tokens", 0)

    return usage

# 保存一问一答两条消息到数据库（用户提问 + 助手回答）
async def save_chat_messages(
    db: AsyncSession,
    conversation_id: str,
    user_message: str,
    assistant_message: str,
    model: str,
    usage: TokenUsage,
):
    await conversation_repository.add_message(
        db=db,
        conversation_id=conversation_id,
        role=MessageRole.USER.value,
        content=user_message,
        model=model,
        prompt_tokens=usage.prompt_tokens,
    )

    await conversation_repository.add_message(
        db=db,
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT.value,
        content=assistant_message,
        model=model,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
    )

# 把接口请求转换成调用大模型的统一请求对象（model 由调用方兜底后传入）
def build_llm_request_from_chat_request(
    request: ChatRequest,
    model: str,
) -> LLMRequest:
    return LLMRequest(
        model=model,
        messages=build_prompt_messages_for_chat(request),
        temperature=request.temperature,
        stream=request.stream,
    )

# 构造最终发给模型的消息列表：请求里自带系统提示词就原样透传，否则按场景渲染模板
def build_prompt_messages_for_chat(request: ChatRequest) -> list[LLMMessage]:
    has_system_message = any(
        message.role == MessageRole.SYSTEM
        for message in request.messages
    )

    if has_system_message:
        return [
            LLMMessage(
                role=LLMRole(message.role.value),
                content=message.content,
            )
            for message in request.messages
        ]

    latest_user_message = get_latest_user_message(request)

    if request.prompt_scenario == PromptScenario.ECOMMERCE_CUSTOMER_SERVICE.value:
        return prompt_service.render_by_scenario(
            scenario=PromptScenario.ECOMMERCE_CUSTOMER_SERVICE,
            version=request.prompt_version or "v1",
            variables={
                "user_question": latest_user_message,
                "business_rules": request.metadata.get(
                    "business_rules",
                    "暂无额外业务规则。",
                ),
                "order_info": request.metadata.get(
                    "order_info",
                    "用户未提供订单信息。",
                ),
            },
        )

    return prompt_service.render_by_scenario(
        scenario=PromptScenario.GENERAL_CHAT,
        version=request.prompt_version or "v1",
        variables={
            "user_question": latest_user_message,
        },
    )

# 取最后一条用户消息作为当前问题；一条用户消息都没有时，用最后一条消息兜底
def get_latest_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == MessageRole.USER:
            return message.content

    return request.messages[-1].content

# 模拟生成引用来源：仅当问题提到 RAG 或知识库时才返回（演示用假数据）
def build_mock_sources(question: str) -> list[SourceDocument]:
    if "RAG" not in question and "知识库" not in question:
        return []

    return [
        SourceDocument(
            document_id="doc_001",
            title="企业知识库说明文档",
            content="RAG 是 Retrieval Augmented Generation，用于结合外部知识增强大模型回答。",
            score=0.89,
            metadata={
                "source": "mock",
                "page": 1,
            },
        )
    ]
