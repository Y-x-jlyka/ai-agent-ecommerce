from pydantic import Field, BaseModel, ConfigDict, field_validator


# 演示：评论请求体（含字段校验）
class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str= Field(...,min_langth=2,descrption="评论内容")
    rating: int= Field(...,ge=1,le=5,descrption="评分")
    @field_validator("content")
    @classmethod
    # 校验评论内容，包含违禁词则报错
    def chat_content(cls,value:str):
        if "垃圾广告" in value:
            raise ValueError("评论包含违禁词")
        return value


# 演示：统一响应体（code/message/data）
class ChatResponse(BaseModel):
    code:int=Field(default=200,description="状态码")
    message:str=Field(...,description="操作状态")
    data:dict=Field(default_factory=dict,description="具体返回数据")
response=ChatResponse(message="这本书真不错",data={"content":"这本书真不错","rating":5})
print("正在返回数据")
print(response.model_dump())

