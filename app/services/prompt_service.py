from app.llm.schemas import LLMMessage
from app.prompts.base import PromptScenario, PromptTemplate
from app.prompts.registry import prompt_registry
from app.prompts.renderer import render_prompt


class PromptService:#封装仓库和渲染，对外提供的借口
    # 按 ID 和版本获取 Prompt 模板
    def get_prompt(
        self,
        prompt_id: str,
        version: str = "v1",
    ) -> PromptTemplate:#底层调用仓库get方法拿到模版
        return prompt_registry.get(prompt_id=prompt_id, version=version)

    def list_prompts(self) -> list[PromptTemplate]:#用list方法拿到所有模版
        return prompt_registry.list()

    # 按 ID 渲染 Prompt，返回消息列表
    def render_by_prompt_id(
        self,
        prompt_id: str,
        variables: dict,
        version: str = "v1",#通过ID拿到模版，渲染后返回最终消息列表
    ) -> list[LLMMessage]:
        prompt = prompt_registry.get(
            prompt_id=prompt_id,
            version=version,
        )

        return render_prompt(
            prompt=prompt,
            variables=variables,
        )

    # 按场景渲染 Prompt，返回消息列表
    def render_by_scenario(
        self,
        scenario: PromptScenario,
        variables: dict,
        version: str = "v1",
    ) -> list[LLMMessage]:#通过场景拿到模版，渲染后返回最终消息列表
        prompt = prompt_registry.find_by_scenario(
            scenario=scenario,
            version=version,
        )

        return render_prompt(
            prompt=prompt,
            variables=variables,
        )


prompt_service = PromptService()