from typing import Optional


# LLM 调用异常基类
class LLMProviderError(Exception):
    # 保存错误信息、厂商、状态码和原始错误
    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        raw_error: Optional[str] = None,
    ):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.raw_error = raw_error

        super().__init__(message)


# 配置错误：如 API Key 未配置
class LLMProviderConfigError(LLMProviderError):
    pass


# 调用超时错误
class LLMProviderTimeoutError(LLMProviderError):
    pass


# 响应解析失败错误
class LLMProviderResponseParseError(LLMProviderError):
    pass