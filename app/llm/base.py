from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.llm.schemas import LLMRequest, LLMResponse, LLMStreamChunk


# LLM Provider 抽象基类：规定所有厂商必须实现的方法
class BaseLLMProvider(ABC):
    @abstractmethod
    # 抽象方法：非流式对话，返回完整响应
    async def chat(self, request: LLMRequest) -> LLMResponse:
        pass

    @abstractmethod
    # 抽象方法：流式对话，逐块产出内容
    async def stream_chat(
        self,
        request: LLMRequest,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        pass