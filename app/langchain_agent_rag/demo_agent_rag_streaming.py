import asyncio

from app.langchain_agent_rag.factory import build_ecommerce_agent_with_rag
from app.langchain_agent_rag.index import ensure_rag_index


# 演示带知识库的 Agent 流式执行：每个节点跑完推送一次增量
async def run():
    ensure_rag_index()

    agent = build_ecommerce_agent_with_rag(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    # 必须用 astream：业务工具只注册了异步实现（coroutine），
    # 同步 stream 会让 ToolNode 走 sync 路径，报
    # NotImplementedError: StructuredTool does not support sync invocation
    async for chunk in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "我的订单 10002 还没发货，这种情况可以退款吗？",
                }
            ]
        },
        stream_mode="updates",
    ):
        print("chunk:")
        print(chunk)
        print("=" * 80)


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
