from langchain_core.prompts import ChatPromptTemplate

# 演示模板变量：查看必填变量、可选变量与已绑定变量
def main():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 {role_name}。"),
        ("human", "请回答用户问题：{user_question}"),
    ])

    # input_variables：调用时必须提供的变量
    # optional_variables：可以不提供的变量（如 MessagesPlaceholder）
    # partial_variables：已经用 partial 绑定过的变量
    print("input_variables:", prompt.input_variables)
    print("optional_variables:", prompt.optional_variables)
    print("partial_variables:", prompt.partial_variables)

    prompt_value = prompt.invoke({
        "role_name": "AI Agent 课程助教",
        "user_question": "为什么 Prompt 需要工程化管理？",
    })

    for message in prompt_value.messages:
        print(message.type, ":", message.content)

if __name__ == "__main__":
    main()
