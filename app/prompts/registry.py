from app.prompts.agent import AGENT_PLANNER_PROMPT_V1
from app.prompts.base import PromptScenario, PromptTemplate
from app.prompts.ecommerce import ECOMMERCE_CUSTOMER_SERVICE_PROMPT_V1,ECOMMERCE_CUSTOMER_SERVICE_PROMPT_V2
from app.prompts.rag import RAG_QA_PROMPT_V1
from app.prompts.templates import GENERAL_CHAT_PROMPT_V1
from app.prompts.structured import (
    AGENT_PLAN_STRUCTURED_PROMPT_V1,
    INTENT_CLASSIFICATION_STRUCTURED_PROMPT_V1,
    RAG_STRUCTURED_ANSWER_PROMPT_V1,
)


class PromptRegistry:#注册表管理器
    def __init__(self):#初始化
        self._prompts: dict[str, PromptTemplate] = {}

    def register(self, prompt: PromptTemplate):#按照ID和版本号生成唯一键存入字典
        key = self._build_key(prompt.prompt_id, prompt.version)
        self._prompts[key] = prompt

    def get(self, prompt_id: str, version: str = "v1") -> PromptTemplate:#根据指定ID和版本号查找并返回对应模版
        key = self._build_key(prompt_id, version)

        if key not in self._prompts:
            raise KeyError(f"Prompt 不存在：{prompt_id}@{version}")

        return self._prompts[key]

    def list(self) -> list[PromptTemplate]:#返回所有prompt模版组成的列表
        return list(self._prompts.values())

    # 按场景和版本查找 Prompt 模板
    def find_by_scenario(
        self,
        scenario: PromptScenario,
        version: str = "v1",
    ) -> PromptTemplate:#查找并返回匹配模版找不到报错
        for prompt in self._prompts.values():
            if prompt.scenario == scenario and prompt.version == version:
                return prompt

        raise KeyError(f"场景 Prompt 不存在：{scenario}@{version}")

    @staticmethod #静态方法
    def _build_key(prompt_id: str, version: str) -> str:#拼接prompt ID和版本号
        return f"{prompt_id}@{version}"


prompt_registry = PromptRegistry()

prompt_registry.register(GENERAL_CHAT_PROMPT_V1)
prompt_registry.register(ECOMMERCE_CUSTOMER_SERVICE_PROMPT_V1)
prompt_registry.register(RAG_QA_PROMPT_V1)
prompt_registry.register(AGENT_PLANNER_PROMPT_V1)
prompt_registry.register(ECOMMERCE_CUSTOMER_SERVICE_PROMPT_V2)
prompt_registry.register(INTENT_CLASSIFICATION_STRUCTURED_PROMPT_V1)
prompt_registry.register(RAG_STRUCTURED_ANSWER_PROMPT_V1)
prompt_registry.register(AGENT_PLAN_STRUCTURED_PROMPT_V1)