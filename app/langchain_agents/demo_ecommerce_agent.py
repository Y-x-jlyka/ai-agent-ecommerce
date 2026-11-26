import asyncio
import json

from app.langchain_agents.factory import (
    build_ecommerce_agent,
    parse_agent_result,
)

# 演示电商客服 Agent：模型自主决定调用哪个工具，再基于工具结果生成回答
async def run():
    agent = build_ecommerce_agent(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    # 必须用 ainvoke：三个工具只注册了异步实现（coroutine），
    # 同步 invoke 会让 ToolNode 走 sync 路径，报
    # NotImplementedError: StructuredTool does not support sync invocation
    result = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": "帮我查一下订单 10001 到哪了？",
            }
        ]
    })

    # ainvoke 返回的结构与 invoke 相同，解析逻辑可以复用
    parsed = parse_agent_result(result)

    print(json.dumps(
        parsed.model_dump(),
        ensure_ascii=False,
        indent=2,
    ))

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
