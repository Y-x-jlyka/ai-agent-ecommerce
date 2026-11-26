from datetime import datetime
from enum import Enum
from pydantic import BaseModel,Field
from app.schemas.chat import ChatRequest, ChatMessage
# 会话状态枚举（正常/归档/已删除）
class ConversationStatus(str,Enum):
    ACTIVE="active"
    ARCHIVED="archived"
    DELETED="deleted"
# 创建会话的请求体
class ConversationCreateRequest(BaseModel):
    title:str=Field(...,min_length=1,max_length=100,description="会话标题")
# 会话信息响应体
class ConversationResponse(BaseModel):
    conversation_id:str=Field(...,description="会话ID")
    title:str=Field(...,description="会话标题")
    status:ConversationStatus=Field(default=ConversationStatus.ACTIVE,description="会话状态")
    created_at:datetime=Field(default_factory=datetime.now,description="创建时间")
    updated_at:datetime=Field(default_factory=datetime.now,description="更新时间")
# 会话消息列表响应体
class ConversationMessagesResponse(BaseModel):
    conversation_id:str=Field(...,description="会话ID")
    messages:list[ChatMessage]=Field(default_factory=list,description="消息列表")