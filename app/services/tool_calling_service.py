import json

from app.core.exceptions import AppException, ErrorCode
from app.core.logging import get_logger
from app.llm.base import BaseLLMProvider
from app.llm.errors import LLMProviderError
from app.llm.schemas import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMRole,
)
from app.tools.executor import ToolExecutionError, tool_executor
from app.tools.registry import tool_registry

logger = get_logger(__name__)

class ToolCallingService:#工具调用服务：组织"模型决定工具 → 执行工具 → 模型总结"的两阶段流程
    # 执行带工具调用的对话：先让模型决定是否调工具，执行完再让模型基于结果生成最终回答
    async def run_with_tools(
        self,
        user_question: str,
        model: str,
        llm_provider: BaseLLMProvider,
    ) -> dict:
        messages = [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content=(
                    "你是一个跨境电商客服助手。\n"
                    "当用户询问订单、物流、发货状态时，优先调用工具查询真实信息。\n"
                    "不要编造订单状态、物流单号或退款进度。\n"
                    "工具返回结果后，请用礼貌、简洁的中文回复用户。"
                ),
            ),
            LLMMessage(
                role=LLMRole.USER,
                content=user_question,
            ),
        ]

        # 第一次调用：把可用工具清单一起发给模型，由模型自己决定是否调用
        first_request = LLMRequest(
            model=model,
            messages=messages,
            temperature=0.1,
            stream=False,
            tools=tool_registry.to_openai_tools(),
            tool_choice="auto",
        )

        try:
            first_response = await llm_provider.chat(first_request)

        except LLMProviderError as exc:
            raise AppException(
                message="工具调用前模型请求失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "provider": exc.provider,
                    "status_code": exc.status_code,
                },
            ) from exc

        # 模型没有要求调用工具：说明这个问题可以直接回答，原样返回即可
        if not first_response.tool_calls:
            return {
                "answer": first_response.content,
                "tool_calls": [],
                "tool_results": [],
                "usage": first_response.usage.model_dump(),
            }

        tool_results = []

        # 逐个执行模型要求的工具；执行失败也当作一种结果，交给模型自行处理
        for tool_call in first_response.tool_calls:
            try:
                result = await tool_executor.execute(
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                )

            except ToolExecutionError as exc:
                logger.warning(
                    f"tool_call_failed tool_name={exc.tool_name} detail={exc.detail}"
                )

                result_content = {
                    "success": False,
                    "error": exc.message,
                    "detail": exc.detail,
                }

            else:
                result_content = {
                    "success": True,
                    "data": result.model_dump(),
                }

            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "tool_name": tool_call.name,
                    "arguments": tool_call.arguments,
                    "result": result_content,
                }
            )

            # 把工具结果以 tool 角色追加进对话历史，模型才能在第二轮看到它
            messages.append(
                LLMMessage(
                    role=LLMRole.ASSISTANT,
                    content="",
                )
            )

            messages.append(
                LLMMessage(
                    role=LLMRole.TOOL,
                    tool_call_id=tool_call.id,
                    content=json.dumps(
                        result_content,
                        ensure_ascii=False,
                    ),
                )
            )

        # 第二次调用：带上工具执行结果，让模型总结成一句自然语言回复
        second_request = LLMRequest(
            model=model,
            messages=messages,
            temperature=0.3,
            stream=False,
        )

        try:
            final_response: LLMResponse = await llm_provider.chat(second_request)

        except LLMProviderError as exc:
            raise AppException(
                message="工具调用后模型总结失败",
                code=ErrorCode.LLM_CALL_FAILED,
                status_code=500,
                data={
                    "provider": exc.provider,
                    "status_code": exc.status_code,
                },
            ) from exc

        return {
            "answer": final_response.content,
            "tool_calls": [
                tool_call.model_dump()
                for tool_call in first_response.tool_calls
            ],
            "tool_results": tool_results,
            "usage": {
                "first": first_response.usage.model_dump(),
                "final": final_response.usage.model_dump(),
            },
        }

tool_calling_service = ToolCallingService()#全局单例：无状态服务，供接口与对话服务复用
