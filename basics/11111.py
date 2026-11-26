from typing import Optional, Union
from urllib import request

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., min_length=1, description="消息内容")


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage] = Field(..., min_length=1, description="对话消息")
    model: str = Field(default="deepseek-chat", description="模型名称")
    # 将 float | int 替换为 Union[float, int] 以兼容老版本 Python
    temperature: Union[float, int] = Field(default=0.7, ge=0, le=2, description="温度")
    stream: bool = Field(default=True, description="是否流式输出")
    session_id: Optional[str] = Field(default=None, description="会话 ID")

    @field_validator("model")
    @classmethod
    def validate(cls, value: str) -> str:
        supported_models = ["deepseek-chat", "qwen-plus", "gpt-4o-mini"]
        if value not in supported_models:
            raise ValueError(f"不支持模型{value}")
        return value


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI回答")
    model: str = Field(..., description="模型名称")
    session_id: Optional[str] = Field(default=None, description="会话 ID")


request = ChatRequest(messages=[ChatMessage(role=MessageRole.SYSTEM, content="你是一个专业的AI助手")])
response = ChatResponse(answer="AI Agent 是能够感知任务，规划步骤并调用工具完成目标的智能体",
                        model=request.model,
                        session_id=request.session_id)

print(request.model_dump())
print(response.model_dump(exclude_none=True))


from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, field_validator


class ToolName(str, Enum):
    QUERY_ORDER = "query_order"
    QUERY_PRODUCT = "query_product"
    QUERY_LOGISTICS = "query_logistics"


class ToolCall(BaseModel):
    tool_name: ToolName = Field(..., description="工具名称")
    arguments: dict[str, Any] = Field(default_factory=dict, description="工具参数")


class OrderQueryArguments(BaseModel):
    order_id: str = Field(..., min_length=1, description="订单 ID")

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("order_id 必须是数字字符串")

        return value


tool_call = ToolCall(
    tool_name=ToolName.QUERY_ORDER,
    arguments={
        "order_id": "10001"
    }
)

order_args = OrderQueryArguments(**tool_call.arguments)

print(tool_call.model_dump())
print(order_args.model_dump())
