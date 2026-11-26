from email import message
from typing import Optional,Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.core.config import settings


# 消息角色枚举（系统/用户/助手/工具）
class MessageRole(str,Enum):
    SYSTEM="system" #角色
    USER="user" #用户
    ASSISTANT="assistant"#ai 回复
    TOOL="tool"#工具调用
# 单条对话消息
class ChatMessage(BaseModel):
    role:MessageRole=Field(...,description="消息角色")
    content:str=Field(...,min_length=1,description="消息内容")
# Token 用量统计
class TokenUsage(BaseModel):
    prompt_tokens:int=Field(default=0,ge=0,description="输出token数")
    completion_tokens:int=Field(default=0,ge=0,description="输出token数")
    total_tokens:int=Field(default=0,ge=0,description="总token数")
# RAG 引用来源文档
class SourceDocument(BaseModel):
    document_id:str=Field(...,description="文档ID")
    title:str=Field(...,description="文档标题")
    content:str=Field(...,description="命中的文档片段")
    score:float=Field(default=0,ge=0,le=1,description="相关性分数")
    metadata:dict[str,Any]=Field(default_factory=dict,description="文档元数据")
# 对话接口请求体
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages:list[ChatMessage]=Field(...,min_length=1,description="对话消息列表")
    model: Optional[str]=Field(default=None,description="模型名称（不传则用 .env 中的默认模型）")
    temperature:float=Field(default=0.7,ge=0,le=2,description="温度")
    stream:bool=Field(default=False,description="是否为流是输出")
    session_id: Optional[str] =Field(default=None,description="会话ID")
    user_id: Optional[str]=Field(default=None,description="用户ID")
    metadata:dict[str,Any]=Field(default_factory=dict,description="扩展元数据")
    prompt_scenario: Optional[str]=Field(default=None,description="prompt场景")
    prompt_version: Optional[str]=Field(default="v1",description="prompt版本")
    @field_validator("model")
    @classmethod
    # 校验模型名（当前仅占位，不做限制）
    def validate_model(cls,value:Optional[str])->Optional[str]:

        # if value not in settings.supported_model_list:
        #     raise ValueError(F"不支持此模型{value}")
        return value
# 对话接口响应体
class ChatResponse(BaseModel):
    answer:str=Field(...,description="AI 回答")
    model:str=Field(...,description="模型名称")
    session_id:Optional[str]=Field(default=None,description="会话ID")
    message_id:Optional[str]=Field(default=None,description="消息ID")
    usage:TokenUsage=Field(default_factory=TokenUsage,description="Token用量")
    sources:list[SourceDocument]=Field(default_factory=list,description="引用来源")
    trace_id:Optional[str]=Field(default=None,description="链路追踪ID")
# 生成标题的请求体
class GenerateTitleRequest(BaseModel):
    message:str=Field(...,min_length=1,max_length=500,description="用户第一条消息")
# 生成标题的响应体
class GenerateTitleResponse(BaseModel):
    title:str=Field(...,description="生成会话标题")