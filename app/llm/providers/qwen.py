from app.core.config import settings
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.schemas import LLMProviderName, LLMRequest


# 通义千问实现（兼容 OpenAI 接口）
class QwenProvider(OpenAICompatibleProvider):
    provider_name = LLMProviderName.QWEN

    # 初始化：传入阿里百炼的 Key、地址和默认模型
    def __init__(self):
        super().__init__(
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_base_url,
            default_model="qwen-plus",
            timeout_seconds=60,
        )

    # 在请求体中追加返回 usage 的参数
    def _build_payload(
        self,
        request: LLMRequest,
        stream: bool,
    ) -> dict:
        payload = super()._build_payload(request=request, stream=stream)

        if stream:
            payload["stream_options"] = {
                "include_usage": True
            }

        return payload