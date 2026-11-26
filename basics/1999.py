import asyncio
from collections.abc import AsyncGenerator
async def fake_llm_stream(prompt:str)->AsyncGenerator[dict[str,str],None]:
    answer=f"根据你的问题{prompt},AI Agent是一个能够理解目标，规划步骤并调用完成任务的智能体"
    for char in answer:
        await asyncio.sleep(0.05)
        yield {"type": "token", "content": char}
    yield{"type":"done","content":""}
async def main():
    async for chunk in fake_llm_stream("什么是AI Agent?"):
        if chunk["type"]=="token":
            print(chunk["content"],end="",flush=True)
        if  chunk["type"]=="done":
            print("\n流式输出结束")
asyncio.run(main())
