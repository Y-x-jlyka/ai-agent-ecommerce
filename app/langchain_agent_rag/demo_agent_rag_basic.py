import asyncio
import json

from app.langchain_agent_rag.factory import (
    build_ecommerce_agent_with_rag,
    parse_agent_rag_result,
)
from app.langchain_agent_rag.index import ensure_rag_index


# 演示带知识库的 Agent：规则类问题查 RAG 知识库，业务类问题调业务工具
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
                "content": "订单未发货时可以退款吗？",
            }
        ]
    })

    # ainvoke 返回结构与 invoke 相同，解析逻辑可复用
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
