import asyncio
import httpx
from pip._internal.cli import status_codes


async def fetch_url(url:str)->str:
    async with httpx.AsyncClient() as client:
        reponse=await  client.get(url)
        return reponse.status_code
async def main():
    status_codes=await fetch_url("https://example.com")
    print(status_codes)
asyncio.run(main())


import asyncio
from collections.abc import AsyncGenerator
async def fake_llm_stream(prompt:str)->AsyncGenerator[str,None]:
    answer=f"根据你的问题{prompt},AI Agent是能够理解目标，规划步骤并调用完成任务的智能体"
    for char in answer:
        await asyncio.sleep(0.05)
        yield char
async def main():
    async for token in fake_llm_stream("什么是AI Agent?"):
        print(token,end="",flush=True)
asyncio.run(main())




