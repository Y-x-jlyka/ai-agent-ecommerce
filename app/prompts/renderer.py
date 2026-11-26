import re
from string import Formatter

from app.llm.schemas import LLMMessage, LLMRole
from app.prompts.base import PromptTemplate


class PromptRenderError(Exception):#Prompt渲染错误
    pass


def extract_variables(template: str) -> set[str]:#提取变量
    variables = set()

    for _, field_name, _, _ in Formatter().parse(template):
        if field_name:
            variables.add(field_name)

    return variables


# 校验变量是否齐全（缺失或多余时报错）
def validate_prompt_variables(
    prompt: PromptTemplate,
    variables: dict,
):#校验提示词变量
    missing = []

    for name in prompt.required_variables:
        if name not in variables or variables[name] is None:
            missing.append(name)

    if missing:
        raise PromptRenderError(
            f"Prompt 缺少必填变量：{', '.join(missing)}"
        )


# 渲染 Prompt：填充变量并输出最终消息列表
def render_prompt(
    prompt: PromptTemplate,
    variables: dict,
) -> list[LLMMessage]:
    validate_prompt_variables(prompt, variables)#渲染提示词

    rendered_messages: list[LLMMessage] = []

    for message_template in prompt.messages:
        try:
            content = message_template.template.format(**variables)
        except KeyError as exc:
            raise PromptRenderError(
                f"Prompt 模板变量未提供：{exc}"
            ) from exc

        rendered_messages.append(
            LLMMessage(
                role=LLMRole(message_template.role.value),
                content=content.strip(),
            )
        )

    return rendered_messages


def mask_prompt_for_log(content: str, max_length: int = 120) -> str:#为日志遮蔽/清理提示词
    content = re.sub(r"\s+", " ", content).strip()

    if len(content) <= max_length:
        return content

    return content[:max_length] + "..."