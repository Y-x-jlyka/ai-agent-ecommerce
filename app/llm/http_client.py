import httpx


# 创建调用大模型的 httpx 异步客户端
def create_llm_http_client(timeout_seconds: float = 60) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        connect=10,
        read=timeout_seconds,
        write=10,
        pool=10,
    )

    return httpx.AsyncClient(timeout=timeout)