import asyncio
import json

from app.langchain_agent_rag.factory import (
    build_ecommerce_agent_with_rag,
    parse_agent_rag_result,
)
from app.langchain_agent_rag.index import ensure_rag_index


# 演示复合场景：订单状态（业务工具）+ 退款规则（知识库工具）组合回答
async def run():
    ensure_rag_index()

    agent = build_ecommerce_agent_with_rag(
        provider="deepseek",
        model_name="deepseek-chat",
    )

    # 必须用 ainvoke：业务工具只注册了异步实现（coroutine），
    # 同步 invoke 会让 ToolNode 走 sync 路径，报
    # NotImplementedError: StructuredTool does not support sync invocation
    result = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": "我的订单 10002 还没发货，这种情况可以退款吗？",
            }
        ]
    })

    parsed = parse_agent_rag_result(result)

    print(json.dumps(
        parsed.model_dump(),
        ensure_ascii=False,
        indent=2,
    ))


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
