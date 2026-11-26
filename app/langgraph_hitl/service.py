from langgraph.types import Command

from app.langgraph_hitl.graph_factory import build_memory_hitl_graph
from app.langgraph_hitl.schemas import create_initial_state


class LangGraphHITLService:
    def __init__(self):
        # 教学版用内存 checkpointer。
        # 生产环境替换成 AsyncPostgresSaver。
        self.graph = build_memory_hitl_graph()

    def build_thread_id(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> str:
        return f"{tenant_id}:{user_id}:{conversation_id}"

    def build_config(
        self,
        thread_id: str,
    ) -> dict:
        return {
            "configurable": {
                "thread_id": thread_id
            }
        }

    def start(
        self,
        user_question: str,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        result = self.graph.invoke(
            create_initial_state(user_question),
            config=config,
        )

        return {
            "thread_id": thread_id,
            "result": result,
        }

    def resume(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
        decision: dict,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        # thread_id 由 tenant+user+conversation 组成，resume 必须能定位到
        # 发起时的那个线程；如果换了一个 user_id，这里会得到一个空线程。
        snapshot = self.graph.get_state(config)
        if not snapshot.next:
            raise ValueError(
                f"会话 {conversation_id} 没有等待人工审核的操作。"
                "请确认 resume 请求使用了与发起时相同的 x-user-id，"
                "或先调用 start 发起退款流程。"
            )

        result = self.graph.invoke(
            Command(resume=decision),
            config=config,
        )

        return {
            "thread_id": thread_id,
            "result": result,
        }

    def get_state(
        self,
        tenant_id: str,
        user_id: str,
        conversation_id: str,
    ) -> dict:
        thread_id = self.build_thread_id(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        config = self.build_config(thread_id)

        snapshot = self.graph.get_state(config)

        return {
            "thread_id": thread_id,
            "values": snapshot.values,
            "next": snapshot.next,
            "config": snapshot.config,
        }


langgraph_hitl_service = LangGraphHITLService()