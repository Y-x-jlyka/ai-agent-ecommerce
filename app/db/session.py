from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from app.core.config import settings

# ==========================================
# 1. 创建异步数据库引擎 (Engine)
# ==========================================
engine = create_async_engine(
    settings.database_url,   # 数据库连接 URL，例如 postgresql+asyncpg://...
    echo=settings.debug,     # 调试模式下开启，会在控制台打印执行的 SQL 语句，便于排查问题
    pool_pre_ping=True       # 连接池预检查：每次从池中取连接前先 ping 一下。防止 MySQL 等数据库因超时自动断开连接导致程序报错
)

# ==========================================
# 2. 创建异步会话工厂 (Session Factory)
# ==========================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False   # 【重点】异步环境必配。设置为 False 后，提交事务(commit)后不会使对象属性过期，避免引发隐式 IO 查询导致 MissingGreenlet 报错
)

# 提示：在实际业务代码中，通常不会直接用这个工厂，而是通过框架（如 FastAPI）的依赖注入（Depends）来生成独立的 Session。