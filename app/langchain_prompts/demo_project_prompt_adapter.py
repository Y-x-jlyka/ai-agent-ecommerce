from langchain_core.messages import BaseMessage

from app.langchain_prompts.service import langchain_prompt_service
from app.prompts.base import PromptScenario
from app.schemas.chat import ChatRequest, MessageRole

# 把请求里的历史消息转成 (角色, 内容) 元组列表，最后一条用户消息留给模板变量
def build_history_from_chat_request(
    request: ChatRequest,
) -> list[BaseMessage]:
    history = []

    # 用 [:-1] 排除最后一条：它才是本轮要回答的问题，不放进 history
    for message in request.messages[:-1]:
        if message.role == MessageRole.USER:
            history.append(("human", message.content))

        elif message.role == MessageRole.ASSISTANT:
            history.append(("ai", message.content))

    return history

# 项目适配层：按场景把请求的 messages 与 metadata 映射成模板变量，渲染成消息列表
def build_langchain_messages_from_chat_request(
    request: ChatRequest,
) -> list[BaseMessage]:
    latest_user_question = ""

    # 倒序找最后一条用户消息，作为本轮问题
    for message in reversed(request.messages):
        if message.role == MessageRole.USER:
            latest_user_question = message.content
            break

    # 未指定场景时默认走通用聊天
    scenario = PromptScenario(request.prompt_scenario or PromptScenario.GENERAL_CHAT.value)

    # 所有场景共用的两个变量：历史对话与当前问题
    variables = {
        "history": build_history_from_chat_request(request),
        "user_question": latest_user_question,
    }

    # 客服场景额外需要业务规则与订单信息，缺省时给兜底文案，避免渲染报错
    if scenario == PromptScenario.ECOMMERCE_CUSTOMER_SERVICE:
        variables["business_rules"] = request.metadata.get(
            "business_rules",
            "暂无额外业务规则。",
        )
        variables["order_info"] = request.metadata.get(
            "order_info",
            "用户未提供订单信息。",
        )

    # RAG 场景需要检索到的知识库片段
    if scenario == PromptScenario.RAG_QA:
        variables["retrieved_context"] = request.metadata.get(
            "retrieved_context",
            "暂无检索上下文。",
        )

    # Agent 规划场景需要目标、工具清单与约束条件
    if scenario == PromptScenario.AGENT_PLANNER:
        variables["user_goal"] = latest_user_question
        variables["available_tools"] = request.metadata.get(
            "available_tools",
            "暂无可用工具。",
        )
        variables["constraints"] = request.metadata.get(
            "constraints",
            "无。",
        )

    # 交给 Prompt 服务按场景 + 版本渲染，返回可直接发给模型的消息列表
    return langchain_prompt_service.render_messages_by_scenario(
        scenario=scenario,
        version=request.prompt_version or "v1",
        variables=variables,
    )
