from dataclasses import asdict
from typing import Any, Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.rag_core import AdvancedRetrievalRequest, RetrievalConfig, RetrievalMode, advanced_retrieval_service
from app.schemas.response import ApiResponse
router = APIRouter()
class AdvancedRetrievalApiRequest(BaseModel):
    query: str = Field(..., min_length=1)
    mode: Literal['vector','keyword','hybrid'] = 'hybrid'
    top_k: int = Field(default=5, ge=1, le=20)
    candidate_k: int = Field(default=20, ge=1, le=100)
    vector_weight: float = Field(default=0.7, ge=0, le=1)
    keyword_weight: float = Field(default=0.3, ge=0, le=1)
    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True
    min_score: float = Field(default=0.05, ge=0)
    max_context_chars: int = Field(default=2000, ge=100)
    metadata_filter: dict[str, Any] | None = None
@router.post('/knowledge/advanced-search', response_model=ApiResponse[dict])
async def advanced_search(req: AdvancedRetrievalApiRequest):
    cfg = RetrievalConfig(RetrievalMode(req.mode), req.top_k, req.candidate_k, req.vector_weight, req.keyword_weight, req.use_query_rewrite, req.use_multi_query, req.use_mmr, req.use_rerank, req.min_score, req.max_context_chars, req.metadata_filter)
    return ApiResponse[dict](data=asdict(advanced_retrieval_service.retrieve(AdvancedRetrievalRequest(req.query, cfg))))
