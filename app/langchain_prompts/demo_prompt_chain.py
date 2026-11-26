from langchain_core.output_parsers import StrOutputParser

from app.langchain_models.model_factory import LangChainModelFactory
from app.langchain_prompts.templates import GENERAL_CHAT_PROMPT

# 演示 LCEL 链：提示词模板 → 模型 → 字符串解析器，一次 invoke 得到纯文本
def main():
    # 复用项目里统一的模型工厂，换厂商只改 provider，不用改链
    model = LangChainModelFactory.create(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
    )

    # 把模型的 AIMessage 转成纯字符串，省去手动取 .content
    parser = StrOutputParser()

    # | 是 LCEL 管道：上一步的输出自动成为下一步的输入
    chain = GENERAL_CHAT_PROMPT | model | parser

    result = chain.invoke({
        "history": [],
        "user_question": "请用三句话解释 LangChain Prompt 的作用。",
    })

    print(result)

if __name__ == "__main__":
    main()
