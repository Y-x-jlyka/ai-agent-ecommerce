import asyncio

from app.langchain_agents.factory import build_ecommerce_agent

# 演示 Agent 流式执行：stream_mode="updates" 每个节点跑完就推送一次增量
async def run():
    agent = build_ecommerce_agent(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    # 必须用 astream：工具只注册了异步实现（coroutine），
    # 同步 stream 会让 ToolNode 走 sync 路径，报
    # NotImplementedError: StructuredTool does not support sync invocation
    async for chunk in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "帮我查一下订单 10001 到哪了？",
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
