from typing import Any, Optional

from app.schemas.chat import SourceDocument


# 知识库数据访问层：模拟文档检索
class KnowledgeRepository:
    # 模拟检索文档，返回命中片段列表
    async def search_documents(
        self,
        question: str,
        knowledge_base_id: str,
        top_k: int,
        metadata_filter: Optional[dict[str, Any]] = None,
    ) -> list[SourceDocument]:
        return [
            SourceDocument(
                document_id="doc_001",
                title="AI Agent 课程资料",
                content="RAG 是检索增强生成，用于让大模型结合外部知识回答问题。",
                score=0.92,
                metadata={
                    "knowledge_base_id": knowledge_base_id,
                    "page": 1,
                    "filter": metadata_filter or {},
                },
            )
        ][:top_k]


knowledge_repository = KnowledgeRepository()