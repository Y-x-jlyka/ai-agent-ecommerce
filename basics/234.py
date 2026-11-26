import asyncio
async def bfe():
    yield 1
    yield 2
async def main():
    async for a in bfe():
        print(f"取出{a}")
asyncio.run(main())

import asyncio
async def acd():
    print("开始读取数据")
    yield "第一个"
    yield "第二个"
    print("读取结束")
async def main():
    async for b in acd():
        print(f"数据：{b}")

asyncio.run(main())

import asyncio
async def chat():
    print("开始请求AI")
    await asyncio.sleep(1)
    yield "你"
    await asyncio.sleep(1)
    yield "在"
    await asyncio.sleep(1)
    yield "吗"
    print("AI对话完成")
async def main():
    async for b in chat():
        print(f"AI输出:{b}")
asyncio.run(main())
