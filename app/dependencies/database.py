from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
# 演示用的假数据库会话（不真正执行 SQL）
class MockDBSession:
    # 模拟执行 SQL，仅返回提示字符串
    async def execute(self,sql:str)->str:
        return f"执行 AQL:{sql}"
    # 模拟关闭会话
    async def close(self):
        print("关闭MockDBSession")
# 依赖：产出数据库会话，请求结束后自动关闭
async def get_db_session()->AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
