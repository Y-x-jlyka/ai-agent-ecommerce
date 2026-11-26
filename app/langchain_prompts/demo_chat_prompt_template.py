from langchain_core.prompts import ChatPromptTemplate

# 演示 ChatPromptTemplate：system + human 两条消息，渲染后查看消息类型与内容
def main():
    # 用简化写法定义模板：元组第一位是角色，第二位是内容，{topic} 是待填变量
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个专业的 AI Agent 课程助教。",
        ),
        (
            "human",
            "请用三句话解释：{topic}",
        ),
    ])

    # 渲染模板：把变量填进去，得到 ChatPromptValue（不是字符串）
    prompt_value = prompt.invoke({
        "topic": "LangChain Prompt",
    })

    print("prompt_value type:", type(prompt_value))
    print("messages:")

    # 逐条打印渲染后的消息：type 为 system / human，content 为填充后的完整内容
    for message in prompt_value.messages:
        print(message.type, ":", message.content)
        print("-" * 80)

if __name__ == "__main__":
    main()
