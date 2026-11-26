from app.core.config import Settings,get_settings
# 依赖：返回全局配置对象
async def get_app_settings()->Settings:
    return get_settings()