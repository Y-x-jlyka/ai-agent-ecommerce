import uuid

from app.core.logging import get_logger
from app.schemas.chat import SourceDocument, TokenUsage
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.chat_service import logger
from app.core.exceptions import AppException,ErrorCode

logger=get_logger(__name__)


# 知识库问答主流程：检索 + 模拟生成回答
async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:
    logger.info(f"rag_query_start knowledge_base-id={request.knowledge_base_id}top_k-{request.top_k}")
    if request.knowledge_base_id=="kb_error":
        raise AppException(
            message="知识库查询失败",
            code=ErrorCode.RAG_QUERY_FAILED,
            status_code=500,
            data={"knowledge_base_id":request.knowledge_base_id}
            )
    source = SourceDocument(
        document_id="doc_001",
        title="AI Agent 课程资料",
        content="RAG 是检索增强生成，用于让大模型结合外部知识回答问题。",
        score=0.92,
        metadata={
            "knowledge_base_id": request.knowledge_base_id,
            "page": 1,
        },
    )

    answer = f"根据知识库 {request.knowledge_base_id} 的内容，RAG 是检索增强生成。"
    logger.info(f"rag_query_success knowledge_base_id={request.knowledge_base_id}")
    return RAGQueryResponse(
        answer=answer,
        knowledge_base_id=request.knowledge_base_id,
        sources=[source],
        usage=TokenUsage(
            prompt_tokens=len(request.question),
            completion_tokens=len(answer),
            total_tokens=len(request.question) + len(answer),
        ),
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
    )