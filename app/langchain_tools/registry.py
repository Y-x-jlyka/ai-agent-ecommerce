from langchain_core.tools import BaseTool

from app.langchain_tools.tools import ECOMMERCE_LANGCHAIN_TOOLS

class LangChainToolRegistry:#LangChain 工具注册表：管理 BaseTool 实例，供 LangChain 链路使用
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    # 注册工具，以工具名作为唯一键存入表中
    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    # 按名称取工具：不存在时抛 KeyError
    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"工具不存在：{name}")

        return self._tools[name]

    # 返回所有已注册的 LangChain 工具（方法名不能用 list，会遮蔽内置类型导致注解报错）
    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    # 返回全部工具名的列表
    def names(self) -> list[str]:
        return list(self._tools.keys())

    # 按名称列表批量取工具；不传或传空则返回全部
    def get_many(
        self,
        names: list[str] | None = None,
    ) -> list[BaseTool]:
        if not names:
            return self.list_tools()

        return [
            self.get(name)
            for name in names
        ]

langchain_tool_registry = LangChainToolRegistry()

for item in ECOMMERCE_LANGCHAIN_TOOLS:
    langchain_tool_registry.register(item)