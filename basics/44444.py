import asyncio

from types import TracebackType


class AsynDatabase:
    async def __aenter__(self):
        print("打开数据库连接")
        return self
    async def __aexit__(self, exc_type,exc_value,traceback):
        print("关闭数据库连接")
    async def query(self,sql:str)-> str:
        await asyncio.sleep(1)
        return f"查询结果{sql}"
async def main():
    async  with AsynDatabase as db:
        result=await db.query("SELECT*FROM users")
        print(result)
asyncio.run(main())
