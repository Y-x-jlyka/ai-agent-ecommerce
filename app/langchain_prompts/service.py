from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import ChatPromptValue

from app.langchain_prompts.registry import (
    LangChainPromptDefinition,
    langchain_prompt_registry,
)
from app.prompts.base import PromptScenario

class LangChainPromptService:#Prompt 服务层：按 prompt_id 或场景取模板，并渲染成消息列表
    # 按 prompt_id + 版本取模板定义（同时校验是否启用）
    def get_by_prompt_id(
        self,
        prompt_id: str,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        return langchain_prompt_registry.get_by_prompt_id(
            prompt_id=prompt_id,
            version=version,
        )

    # 按场景 + 版本取模板定义（遍历查找第一个匹配且启用的）
    def get_by_scenario(
        self,
        scenario: PromptScenario,
        version: str = "v1",
    ) -> LangChainPromptDefinition:
        return langchain_prompt_registry.get_by_scenario(
            scenario=scenario,
            version=version,
        )

    # 按 prompt_id 渲染出 ChatPromptValue（填充变量后的提示词值对象）
    def render_by_prompt_id(
        self,
        prompt_id: str,
        variables: dict,
        version: str = "v1",
    ) -> ChatPromptValue:
        definition = self.get_by_prompt_id(
            prompt_id=prompt_id,
            version=version,
        )

        return definition.prompt.invoke(variables)

    # 按 prompt_id 渲染并返回消息列表，可直接作为模型的 messages 入参
    def render_messages_by_prompt_id(
        self,
        prompt_id: str,
        variables: dict,
        version: str = "v1",
    ) -> list[BaseMessage]:
        prompt_value = self.render_by_prompt_id(
            prompt_id=prompt_id,
            variables=variables,
            version=version,
        )

        return prompt_value.messages

    # 按场景渲染出 ChatPromptValue
    def render_by_scenario(
        self,
        scenario: PromptScenario,
        variables: dict,
        version: str = "v1",
    ) -> ChatPromptValue:
        definition = self.get_by_scenario(
            scenario=scenario,
            version=version,
        )

        return definition.prompt.invoke(variables)

    # 按场景渲染并返回消息列表，适配层就是走这个入口
    def render_messages_by_scenario(
        self,
        scenario: PromptScenario,
        variables: dict,
        version: str = "v1",
    ) -> list[BaseMessage]:
        prompt_value = self.render_by_scenario(
            scenario=scenario,
            variables=variables,
            version=version,
        )

        return prompt_value.messages

    # 列出全部 Prompt 的概要：变量清单、元数据、标签，供接口直接返回
    def list_prompts(self) -> list[dict]:
        return [
            {
                "prompt_id": definition.prompt_id,
                "name": definition.name,
                "scenario": definition.scenario.value,
                "version": definition.version,
                "description": definition.description,
                "enabled": definition.enabled,
                "input_variables": definition.prompt.input_variables,
                "optional_variables": definition.prompt.optional_variables,
                "metadata": definition.prompt.metadata,
                "tags": definition.prompt.tags,
            }
            for definition in langchain_prompt_registry.list()
        ]

langchain_prompt_service = LangChainPromptService()#全局单例：无状态服务，供接口与适配层复用
