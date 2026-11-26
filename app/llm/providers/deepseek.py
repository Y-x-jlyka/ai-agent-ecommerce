from app.core.config import settings
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.schemas import LLMProviderName


# DeepSeek 厂商实现（兼容 OpenAI 接口）
class DeepSeekProvider(OpenAICompatibleProvider):
    provider_name = LLMProviderName.DEEPSEEK

    # 初始化：传入 DeepSeek 的 Key、地址和默认模型
    def __init__(self):
        super().__init__(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            default_model="deepseek-chat",
            timeout_seconds=60,
        )