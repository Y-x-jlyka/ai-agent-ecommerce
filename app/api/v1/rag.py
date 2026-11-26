from fastapi import APIRouter

from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.schemas.response import ApiResponse
from app.services.rag_service import query_rag

router = APIRouter()


@router.post("/rag/query", response_model=ApiResponse[RAGQueryResponse])
# 知识库问答接口：检索 + 生成回答
async def rag_query(
    request: RAGQueryRequest,
) -> ApiResponse[RAGQueryResponse]:
    result = await query_rag(request)

    return ApiResponse[RAGQueryResponse](
        data=result
    )