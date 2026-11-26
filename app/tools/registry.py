from app.tools.base import ToolDefinition
from app.tools.ecommerce import (
    query_logistics,
    query_order,
    transfer_human,
)
from app.tools.schemas import (
    QueryLogisticsArgs,
    QueryLogisticsResult,
    QueryOrderArgs,
    QueryOrderResult,
    TransferHumanArgs,
    TransferHumanResult,
)

class ToolRegistry:#工具注册表：按名称管理工具，并可导出 OpenAI 格式的工具定义
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    # 注册工具，以工具名作为唯一键存入表中
    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    # 按名称取工具：不存在或已禁用时抛 KeyError
    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"工具不存在：{name}")

        tool = self._tools[name]

        if not tool.enabled:
            raise KeyError(f"工具已禁用：{name}")

        return tool

    # 返回所有已注册的工具（包含已禁用的）
    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    # 导出 OpenAI function calling 格式的工具列表（只导出启用中的工具）
    def to_openai_tools(self) -> list[dict]:
        return [
            tool.to_openai_tool()
            for tool in self._tools.values()
            if tool.enabled
        ]

tool_registry = ToolRegistry()#全局单例：模块导入时即完成下列内置工具的注册

# 内置工具一：按订单号查询订单状态与物流信息
tool_registry.register(
    ToolDefinition(
        name="query_order",
        description="根据订单号查询订单状态和物流信息。当用户询问订单状态、发货状态、物流状态时使用。",
        args_schema=QueryOrderArgs,
        result_schema=QueryOrderResult,
        func=query_order,
    )
)

# 内置工具二：按物流单号查询运输轨迹（用户已提供单号时用）
tool_registry.register(
    ToolDefinition(
        name="query_logistics",
        description="根据物流单号查询物流轨迹。当用户已经提供物流单号，并询问包裹运输状态时使用。",
        args_schema=QueryLogisticsArgs,
        result_schema=QueryLogisticsResult,
        func=query_logistics,
    )
)

# 内置工具三：创建人工客服工单（用户要求转人工或超出 AI 能力时用）
tool_registry.register(
    ToolDefinition(
        name="transfer_human",
        description="当用户明确要求人工客服，或者问题超出 AI 能力范围时创建人工客服工单。",
        args_schema=TransferHumanArgs,
        result_schema=TransferHumanResult,
        func=transfer_human,
    )
)
