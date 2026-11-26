from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


# 按优先级查找 .env 文件并返回绝对路径
def _resolve_env_file() -> str:
    """按优先级查找 .env，避免因为运行目录不同导致配置加载不到。"""
    for candidate in (BASE_DIR / ".env", BASE_DIR / "app" / ".env"):
        if candidate.exists():
            return str(candidate)

    return ".env"


# 全局配置类：从 .env 和环境变量读取所有配置项
class Settings(BaseSettings):
    app_name:str=Field(default="AI Agent Course API")
    app_env:str=Field(default="development")
    app_version:str=Field("0.1.0")
    api_v1_prefix:str=Field(default="/api/v1")
    debug:bool=Field(default=False)
    app_api_key:str=Field(default="dev-api-key-123")
    default_model:str=Field(default="deepseek-chat")
    default_llm_provider: str = Field(default="deepseek")
    supported_models:str=Field(default="deepseek-chat,qwen_plus,gpt-40-mini")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5433/ai_agent_course"
    )
    redis_url: str = Field(default="redis://:redis123@localhost:6379/0")
    redis_default_ttl_seconds: int = Field(default=300)
    rate_limit_window_seconds: int = Field(default=60)
    rate_limit_max_requests: int = Field(default=20)
    openai_api_key: str = Field(default="")
    openai_base_url: str = Field(default="https://api.openai.com/v1")

    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com")

    dashscope_api_key: str = Field(default="")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    model_config = SettingsConfigDict(
        env_file=_resolve_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False)
    @property
    # 把逗号分隔的模型字符串解析成列表
    def supported_model_list(self)->list[str]:
        return [model.strip()
                for model in self.supported_models.split(",")
                if model.strip()]
@lru_cache()
# 获取配置单例（带缓存，只加载一次）
def get_settings()->Settings:
    return Settings()
settings=get_settings()

