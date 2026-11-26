import asyncio

from types import TracebackType

import asyncio
class Chat:
    async def __aenter__(self):
        print("打开文件资源")
        await asyncio.sleep(1)
        return self
    async def __aexit__(self,exc_typ,exc_val,exc_tb):
        print("关闭文件资源")
        await asyncio.sleep(1)
    async def acd(self):
        print("读取文件内容")
async def main():
        async with Chat() as db:
            await db.acd()
asyncio.run(main())
