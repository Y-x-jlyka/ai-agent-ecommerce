from typing import Union

from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.qwen import QwenProvider
from app.llm.schemas import LLMProviderName


# LLM Provider 工厂：根据名称创建对应 Provider
class LLMProviderFactory:
    @staticmethod
    # 根据 Provider 名称创建实例
    def create(provider: Union[LLMProviderName, str, None] = None) -> BaseLLMProvider:
        provider_name = provider or infer_provider_from_model(settings.default_model)

        if isinstance(provider_name, str):
            provider_name = LLMProviderName(provider_name)

        if provider_name == LLMProviderName.DEEPSEEK:
            return DeepSeekProvider()

        if provider_name == LLMProviderName.QWEN:
            return QwenProvider()

        if provider_name == LLMProviderName.OPENAI:
            return OpenAIProvider()

        raise ValueError(f"不支持的 LLM Provider：{provider_name}")


# 根据模型名前缀推断 Provider
def infer_provider_from_model(model: str) -> LLMProviderName:
    if model.startswith("deepseek"):
        return LLMProviderName.DEEPSEEK

    if model.startswith("qwen"):
        return LLMProviderName.QWEN

    if model.startswith("gpt"):
        return LLMProviderName.OPENAI

    return LLMProviderName.DEEPSEEK