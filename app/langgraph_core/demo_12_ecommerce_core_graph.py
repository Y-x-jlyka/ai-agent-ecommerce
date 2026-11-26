"""电商客服核心图（纯规则版）。

不依赖 LLM 与工具，用固定分支演示 StateGraph 的状态流转与条件路由，
与 langchain_agents 里基于 create_agent 的智能体版本形成对照：
同样的业务，图的执行路径是确定性的，Agent 则由模型自主规划。
"""

import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class EcommerceCoreState(TypedDict):#整张图共享的状态；每个节点返回 dict 即为增量更新
    user_question: str          # 用户原始问题
    intent: str                 # 意图分类结果：refund / order / general
    order_id: str | None        # 从问题中提取的订单号，可能缺失
    order_status: str | None    # 查单结果：paid / shipped / not_found
    policy_type: str | None     # 命中的售后规则类型
    policy_answer: str | None   # 售后规则文案
    final_answer: str           # 最终回复
    # Annotated + operator.add：各节点返回的 logs 列表会自动追加合并，而非覆盖
    logs: Annotated[list[str], operator.add]


def classify_intent_node(state: EcommerceCoreState) -> dict:
    # 入口节点：用关键词规则做意图分类（教学用，实际可换成 LLM 分类）
    question = state["user_question"]

    if "退款" in question or "退货" in question:
        intent = "refund"
    elif "订单" in question or "物流" in question:
        intent = "order"
    else:
        intent = "general"

    return {
        "intent": intent,
        "logs": [f"classify_intent：识别意图为 {intent}"],
    }


def route_by_intent(
    state: EcommerceCoreState,
) -> Literal["general", "need_order"]:
    # 条件路由：返回值映射到 add_conditional_edges 传入的目标节点名
    if state["intent"] == "general":
        return "general"

    return "need_order"


def extract_order_id_node(state: EcommerceCoreState) -> dict:
    # 从问题文本中提取订单号；教学用简单包含匹配，未识别则为 None
    question = state["user_question"]

    if "10001" in question:
        order_id = "10001"
    elif "10002" in question:
        order_id = "10002"
    else:
        order_id = None

    return {
        "order_id": order_id,
        "logs": [f"extract_order_id：订单号为 {order_id}"],
    }


def route_after_extract_order_id(
    state: EcommerceCoreState,
) -> Literal["ask_order_id", "query_order"]:
    # 缺订单号就追问用户，有订单号才继续查单
    if not state["order_id"]:
        return "ask_order_id"

    return "query_order"


def ask_order_id_node(state: EcommerceCoreState) -> dict:
    # 追问节点：给出提示语后直接结束本轮
    return {
        "final_answer": "请您提供订单号，我才能继续查询订单状态和售后规则。",
        "logs": ["ask_order_id：缺少订单号，追问用户。"],
    }


def query_order_node(state: EcommerceCoreState) -> dict:
    # 模拟查单：写死两条测试数据，替代真实订单接口
    order_id = state["order_id"]

    if order_id == "10001":
        order_status = "shipped"
        status_text = "已发货"
    elif order_id == "10002":
        order_status = "paid"
        status_text = "已付款，待发货"
    else:
        order_status = "not_found"
        status_text = "未查询到订单"

    return {
        "order_status": order_status,
        "logs": [f"query_order：订单状态为 {status_text}"],
    }


def route_after_query_order(
    state: EcommerceCoreState,
) -> Literal["retrieve_policy", "generate_order_answer"]:
    # 退款意图需要先查售后规则；纯订单查询直接生成回答
    if state["intent"] == "refund":
        return "retrieve_policy"

    return "generate_order_answer"


def decide_policy_type_node(state: EcommerceCoreState) -> dict:
    # 按订单状态决定该查哪条售后规则（未发货可退 / 已发货走退货流程）
    order_status = state["order_status"]

    if order_status == "paid":
        policy_type = "refund_before_shipping"
    elif order_status == "shipped":
        policy_type = "refund_after_shipping"
    else:
        policy_type = "unknown"

    return {
        "policy_type": policy_type,
        "logs": [f"decide_policy_type：规则类型为 {policy_type}"],
    }


def retrieve_policy_node(state: EcommerceCoreState) -> dict:
    # 模拟知识库检索：按规则类型返回固定文案
    policy_type = state["policy_type"]

    if policy_type == "refund_before_shipping":
        policy_answer = "根据售后规则，订单未发货时，用户可以申请取消订单并退款。"
    elif policy_type == "refund_after_shipping":
        policy_answer = "根据售后规则，订单已发货后，需要收到商品后再发起退货退款申请。"
    else:
        policy_answer = "当前状态无法从规则中确认，建议转人工客服。"

    return {
        "policy_answer": policy_answer,
        "logs": ["retrieve_policy：完成售后规则查询。"],
    }


def generate_general_answer_node(state: EcommerceCoreState) -> dict:
    # 普通问题分支：占位回答，实际可接 ChatModel
    return {
        "final_answer": "这是普通问题，后续可以接入普通 ChatModel 生成回答。",
        "logs": ["generate_general_answer：普通回答完成。"],
    }


def generate_order_answer_node(state: EcommerceCoreState) -> dict:
    # 订单查询分支：只汇报订单状态
    order_status = state["order_status"]

    status_map = {
        "paid": "已付款，待发货",
        "shipped": "已发货",
        "not_found": "未查询到订单",
    }

    return {
        "final_answer": f"您的订单当前状态是：{status_map.get(order_status, '未知')}。",
        "logs": ["generate_order_answer：订单回答完成。"],
    }


def generate_refund_answer_node(state: EcommerceCoreState) -> dict:
    # 退款分支：订单状态 + 售后规则拼接成完整回答
    order_status = state["order_status"]

    status_map = {
        "paid": "已付款，待发货",
        "shipped": "已发货",
        "not_found": "未查询到订单",
    }

    return {
        "final_answer": (
            f"您的订单当前状态是：{status_map.get(order_status, '未知')}。"
            f"{state.get('policy_answer')}"
        ),
        "logs": ["generate_refund_answer：退款回答完成。"],
    }


def build_graph():
    # 组装图：注册节点 → 连边（含三处条件路由）→ compile 得到可执行图
    graph = StateGraph(EcommerceCoreState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("extract_order_id", extract_order_id_node)
    graph.add_node("ask_order_id", ask_order_id_node)
    graph.add_node("query_order", query_order_node)
    graph.add_node("decide_policy_type", decide_policy_type_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("generate_general_answer", generate_general_answer_node)
    graph.add_node("generate_order_answer", generate_order_answer_node)
    graph.add_node("generate_refund_answer", generate_refund_answer_node)

    # 入口：所有请求先进意图分类
    graph.add_edge(START, "classify_intent")

    # 路由一：普通问题直达回答；订单/退款类需要先提取订单号
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "general": "generate_general_answer",
            "need_order": "extract_order_id",
        },
    )

    # 路由二：有订单号查单，缺订单号追问后结束
    graph.add_conditional_edges(
        "extract_order_id",
        route_after_extract_order_id,
        {
            "ask_order_id": "ask_order_id",
            "query_order": "query_order",
        },
    )

    # 路由三：退款意图进入规则检索链，纯查询直接生成订单回答
    graph.add_conditional_edges(
        "query_order",
        route_after_query_order,
        {
            "retrieve_policy": "decide_policy_type",
            "generate_order_answer": "generate_order_answer",
        },
    )

    # 退款链的固定顺序：定规则类型 → 查规则 → 生成退款回答
    graph.add_edge("decide_policy_type", "retrieve_policy")
    graph.add_edge("retrieve_policy", "generate_refund_answer")

    # 四个出口节点全部连到 END
    graph.add_edge("ask_order_id", END)
    graph.add_edge("generate_general_answer", END)
    graph.add_edge("generate_order_answer", END)
    graph.add_edge("generate_refund_answer", END)

    return graph.compile()


def main():
    # 用四个问题覆盖全部四条执行路径
    app = build_graph()

    questions = [
        "你好，介绍一下 LangGraph。",                # general 直达回答
        "帮我查一下订单 10001。",                    # 查单 → 订单回答
        "我的订单 10002 还没发货，可以退款吗？",      # 查单 → 规则 → 退款回答
        "我要退款，但是忘记订单号了。",               # 缺订单号 → 追问
    ]

    for question in questions:
        print("question:", question)
        print("=" * 80)

        result = app.invoke({
            "user_question": question,
            "intent": "",
            "order_id": None,
            "order_status": None,
            "policy_type": None,
            "policy_answer": None,
            "final_answer": "",
            "logs": [],
        })

        print("final_answer:", result["final_answer"])
        print("logs:")
        for log in result["logs"]:
            print("-", log)

        print("=" * 120)


if __name__ == "__main__":
    main()
