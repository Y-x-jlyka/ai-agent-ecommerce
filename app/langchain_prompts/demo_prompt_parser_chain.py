from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.langchain_models.model_factory import LangChainModelFactory

class IntentResult(BaseModel):#意图识别结果：意图枚举 + 置信度 + 判断原因
    intent: Literal[
        "query_order",
        "refund",
        "logistics",
        "product_question",
        "human_service",
        "other",
    ] = Field(..., description="用户意图")

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="置信度",
    )

    reason: str = Field(..., description="判断原因")

# 演示结构化输出链：把 Pydantic 的格式说明注入提示词，输出自动解析成对象
def main():
    # 解析器会根据 IntentResult 生成 JSON 格式说明，并负责把模型输出反序列化
    parser = PydanticOutputParser(
        pydantic_object=IntentResult,
    )

    # {format_instructions} 用 partial 提前绑定成解析器给出的格式要求
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个电商客服意图识别器。\n"
                "你必须根据格式要求输出。\n"
                "{format_instructions}"
            ),
        ),
        (
            "human",
            "用户问题：{user_question}",
        ),
    ]).partial(
        format_instructions=parser.get_format_instructions()
    )

    # 意图分类属于确定性任务，temperature 设为 0 让结果尽量稳定
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0,
    )

    # 链的最后一步是解析器：模型返回的 JSON 文本会被转成 IntentResult 对象
    chain = prompt | model | parser

    result = chain.invoke({
        "user_question": "我的订单怎么还没发货？",
    })

    print(result.model_dump())

if __name__ == "__main__":
    main()
