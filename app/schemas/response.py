from typing import Generic, TypeVar, Optional, Union

from pydantic import BaseModel,Field
T=TypeVar("T")
# 统一成功响应信封（code/message/data/trace_id）
class ApiResponse(BaseModel,Generic[T]):
    code:int=Field(default=0,description="业务状态码")
    message:str=Field(default="success",description="提示信息")
    data:T=Field(default=None,description="响应数据")
    trace_id: Optional[str] =Field(default=None, description="链路追踪ID")
# 单个字段的错误详情
class ErrorDetail(BaseModel):
    field: Optional[str]=Field(default=None,description="错误字段")
    message:str=Field(...,description="错误信息")
# 统一错误响应体
class ErrorResponse(BaseModel):
    code:int=Field(default=500,description="错误码")
    message:str=Field(...,description="错误信息")
    detail: Union[dict, list, None] =Field(default=None, description="错误详情")
    trace_id:Optional[str]=Field(default=None,description="链路追踪ID")



