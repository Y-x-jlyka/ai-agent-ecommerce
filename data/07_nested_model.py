# from typing import Any
# from typing_extensions import Self
#
# from pydantic import BaseModel,Field
# class Message(BaseModel):
#     role:str
#     content:str=Field(...,min_length=1,description="消息内容")
# class ChatRequest(BaseModel):
#     messages:list[Message]=Field(...,description="对话消息列表")
#     model:str=Field(default="deepseek-chat",description="模型名称")
# request=ChatRequest(messages=[Message(role="system",content="你是个专业的AI助手")
# ,Message(role="user",content="什么是AI助手")])
# print(request.model_dump())
#
# from pydantic import BaseModel,Field,ValidationError
# class ChatRequest(BaseModel):
#     session_id:str=Field(alias="sessionId")
#     message:str
# request=ChatRequest(sessionId="10001",message="你好")
# print(request.session_id)
# print(request.model_dump())
# print(request.model_dump(by_alias=True))
#
# from pydantic import BaseModel,ConfigDict,Field
# class ChatRequest(BaseModel):
#     model_config =ConfigDict(populate_by_name=True)
#     session_id:str=Field(alias="sessionId")
#     message:str
# request1=ChatRequest(session_id="10001",message="你好")
# request2=ChatRequest(sessionId="10002",message="你好")
# print(request1.model_dump())
# print(request2.model_dump())
#
#
# from pydantic import BaseModel,ConfigDict,Field,ValidationError
# class ChatRequest(BaseModel):
#     model_config = ConfigDict(extra="forbid")
#     message:str
#     model:str="deepseek-chat"
# try:
#     request=ChatRequest(message="你好",model="deepseek-chat",unkown_field="xxx")
# except ValidationError as a:
#     print(a)
from email import message_from_binary_file
from typing import Optional
from urllib import request

# from pydantic import BaseModel,Field,ValidationError,field_validator
# class ChatRequest(BaseModel):
#     message:str=Field(...,min_length=1)
#     @field_validator("message")
#     @classmethod
#     def validate_message(cls,value:str)-> str:
#         if "广告" in value:
#             raise ValidationError("message 不能包含广告内容")
#         return  value
# try:
#     request=ChatRequest(message="这是一条广告")
# except ValidationError as e:
#     print(e)

# from pydantic import BaseModel,Field,ValidationError,model_validator
# from typing import Optional
# class ChatRequest(BaseModel):
#     message:str
#     stream:bool=True
#     callback_url: Optional[str] =None
#     @model_validator(mode="after")
#     def validate_callback_url(self):
#         if self.stream is False and self.callback_url is None:
#             raise ValueError("非主流式任务必须提供 callback_url")
#         return self
# try:
#     request=ChatRequest(message="生成一份报告",stream=False)
# except ValidationError as e:
#     print(e)

from pydantic import BaseModel
from typing import Optional
class Chaurequest(BaseModel):
    answer:str
    session_id: Optional[str] =None
    trace_id:Optional[str]=None
request=Chaurequest(answer="你好，我是AI助手")
print(request.model_dump())
print(request.model_dump(exclude_none=True))

from pydantic import BaseModel
class User(BaseModel):
    id:int
    name:str
    email:str
    password:str
user=User(id=1,name="大伟",email="dawei@example.com",password="123456")
print(user.model_dump(exclude={"password"}))
print(user.model_dump(include={"id", "name"}))
