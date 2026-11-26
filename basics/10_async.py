import asyncio
from pickletools import read_int4
from urllib import request, response


async def fetch_data():
    print("开始获取数据")
    await asyncio.sleep(1)
    print("数据获取完成")
    return "这是数据"
result=asyncio.run(fetch_data())
print(result)

import _asyncio
async def query_user():
    await asyncio.sleep(1)
    return "用户信息"
async def query_order():
    await asyncio.sleep(1)
    return "订单信息"
async def query_llm():
    await asyncio.sleep(1)
    return "AI回答"
async def main():
    user,order,answer=await asyncio.gather(query_user(),query_order(),query_llm())
    print(user)
    print(order)
    print(answer)
asyncio.run(main())

import asyncio
async def generate_tokens():
    tokens=["你","好","，","我","是","AI","。"]
    for token in tokens:
        await asyncio.sleep(1)
        yield token
async def main():
    async for token in generate_tokens():
        print(token,end="",flush=True)

asyncio.run(main())

import asyncio
class AsyncDatabase:
    async def __aenter__(self):
        print("打开数据库连接")
        return self
    async def __aexit__(self,exc_type,exc_value,traceback):
        print("关闭数据库连接")
    async def query(self,sql:str)->str:
        await asyncio.sleep(0.5)
        return f"查询结果{sql}"
async def main():
    async with AsyncDatabase() as db:
        result=await db.query("SELECT*FROM users")
        print(result)
asyncio.run(main())

import _asyncio
from pydantic import BaseModel
class ChatRequest(BaseModel):
    message:str
    model:str="deepseek-chat"
    temperature:float=0.7
class ChatResponse(BaseModel):
    answer:str
    model:str
async def call_llm(message:str,model:str,temperature:float) ->str:
     print("正在调试大模型...")
     print(f"模型:{model}")
     print(f"温度{temperature}")
     print(f"用户问题{message}")
     await asyncio.sleep(1)
     return f"你刚才问的问题是：{message}"
async def chat(request:ChatRequest) ->ChatResponse:
     answer= await call_llm(message=request.message,model=request.model,
    temperature=request.temperature)
     return ChatResponse(answer=answer,model=request.model)
async def main():
     request=ChatRequest(message="什么是AI Agent?",model="deepseek-chat",temperature=0.7)
     response=await chat(request)
     print(response.model_dump())
asyncio.run(main())

import asyncio
async def stream_llm_answer(message:str):
    answer=f"这是针对{message}的模拟AI流式回答"
    for char in answer:
        await asyncio.sleep(0.5)
        yield char
async def main():
    async for chunk in stream_llm_answer("什么是RAG"):
        print(chunk,end="",flush=True)
    print()
asyncio.run(main())

