from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message:str
    session_id:Optional[str]=None

request=ChatRequest(message="你好")

print(request.message)
print(request.session_id)
print(request.model_dump())

from typing import Optional
from pydantic import BaseModel, ValidationError

class ChatRequest(BaseModel):
    message:int
    session_id:Optional[str]=None
try:
    request=ChatRequest(message=123)
except ValidationError as e:
    print(e)


from pydantic import BaseModel
class Message(BaseModel):
    role:str
    content:str
class ChatRequest(BaseModel):
    messages:list[Message]
    model:str="deepseeek-chat"

request=ChatRequest(messages=[Message(role="system",content="你是一个AI助手"),
     Message(role="user",content="你好")])
print((request.model_dump()))

fruits=["苹果","香蕉","橘子"]
for index,fruit in enumerate(fruits):
    print(f"{index}:{fruit}")
