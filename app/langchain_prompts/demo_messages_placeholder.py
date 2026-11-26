from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 演示 MessagesPlaceholder：把历史对话按顺序插入 system 与 human 之间
def main():
    # optional=True 表示 history 可以不传；不写则调用时必须提供
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个专业 AI Agent 课程助教。",
        ),
        MessagesPlaceholder(
            variable_name="history",
            optional=True,
        ),
        (
            "human",
            "{user_question}",
        ),
    ])

    # 模拟历史对话：一问一答两条消息，会被整体展开插入到占位符位置
    history = [
        HumanMessage(content="什么是 AI Agent？"),
        AIMessage(content="AI Agent 是可以理解目标、规划步骤并调用工具的智能体。"),
    ]

    prompt_value = prompt.invoke({
        "history": history,
        "user_question": "那 LangChain 和 AI Agent 有什么关系？",
    })

    # 输出应为 4 条：system、human（历史）、ai（历史）、human（当前问题）
    for message in prompt_value.messages:
        print(message.type, ":", message.content)
        print("-" * 80)

if __name__ == "__main__":
    main()
