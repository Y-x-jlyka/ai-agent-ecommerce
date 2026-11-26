from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

# 演示 partial：把角色、日期、回答风格提前绑定，调用时只传 user_question
def main():
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "你是一个专业的 {role_name}。\n"
                "当前日期：{current_date}\n"
                "回答要求：{answer_style}"
            ),
        ),
        (
            "human",
            "{user_question}",
        ),
    ])

    # 预先绑定固定变量：日期在绑定这一刻就算好，之后每次调用都不用再传
    prompt = prompt.partial(
        role_name="AI Agent 课程助教",
        current_date=datetime.now().strftime("%Y-%m-%d"),
        answer_style="口语化、结构清晰、不要编造。",
    )

    # 绑定后：必填变量只剩 user_question，已绑定的变量进入 partial_variables
    print("input_variables:", prompt.input_variables)
    print("partial_variables:", prompt.partial_variables)

    prompt_value = prompt.invoke({
        "user_question": "为什么 Prompt 需要版本管理？",
    })

    for message in prompt_value.messages:
        print(message.type, ":", message.content)
        print("-" * 80)

if __name__ == "__main__":
    main()
