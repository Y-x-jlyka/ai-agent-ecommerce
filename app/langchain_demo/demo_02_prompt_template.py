from langchain_core.prompts import ChatPromptTemplate

def run_prompt_template():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "你是一个专业的 {role_name}，回答要简洁、准确。",
        ),
        (
            "human",
            "请解释一下：{question}",
        ),
    ])

    result = prompt.invoke({
        "role_name": "AI Agent 课程助教",
        "question": "为什么需要 LangChain？",
    })

    print("prompt result type:", type(result))
    print("messages:")
    for message in result.messages:
        print(message.type, ":", message.content)

if __name__ == "__main__":
    run_prompt_template()