from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.rag_core import RetrievalMode, rag_evaluation_service
from app.schemas.response import ApiResponse
router = APIRouter()
class EvaluationRequest(BaseModel):
    mode: Literal['vector','keyword','hybrid'] = 'hybrid'
    top_k: int = Field(default=3, ge=1, le=20)
    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True
@router.get('/rag-evaluation/cases', response_model=ApiResponse[list[dict]])
async def list_evaluation_cases(): return ApiResponse[list[dict]](data=rag_evaluation_service.list_cases())
@router.post('/rag-evaluation/retrieval', response_model=ApiResponse[dict])
async def evaluate_retrieval(req: EvaluationRequest): return ApiResponse[dict](data=rag_evaluation_service.evaluate_retrieval(RetrievalMode(req.mode), req.top_k, req.use_query_rewrite, req.use_multi_query, req.use_mmr, req.use_rerank))
@router.post('/rag-evaluation/generation', response_model=ApiResponse[dict])
async def evaluate_generation(req: EvaluationRequest): return ApiResponse[dict](data=rag_evaluation_service.evaluate_generation(RetrievalMode(req.mode), req.top_k, req.use_query_rewrite, req.use_multi_query, req.use_mmr, req.use_rerank))
@router.post('/rag-evaluation/full-report', response_model=ApiResponse[dict])
async def full_report(): return ApiResponse[dict](data=rag_evaluation_service.run_full_report())
