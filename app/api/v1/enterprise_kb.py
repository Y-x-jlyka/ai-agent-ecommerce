from dataclasses import asdict
from typing import Any, Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.dependencies.auth import get_current_user
from app.rag_core import ChunkStrategy, FeedbackRating, KnowledgeChatRequest, enterprise_kb_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
router = APIRouter()
class IndexFileApiRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = 'tenant_001'
    doc_type: str | None = None
    department: str | None = None
    version: str = 'v1'
    chunk_strategy: Literal['fixed_size','paragraph','page','element','heading','table_aware','code_aware'] = 'heading'
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)
class ChatApiRequest(BaseModel):
    question: str = Field(..., min_length=1)
    tenant_id: str = 'tenant_001'
    top_k: int = Field(default=3, ge=1, le=20)
    metadata_filter: dict[str, Any] | None = None
class FeedbackApiRequest(BaseModel):
    query_id: str = Field(..., min_length=1)
    tenant_id: str = 'tenant_001'
    rating: Literal['good','bad','unknown'] = 'unknown'
    comment: str = ''
@router.post('/enterprise-kb/documents/index-file', response_model=ApiResponse[dict])
async def index_file(req: IndexFileApiRequest, current_user: CurrentUser = Depends(get_current_user)):
    res = enterprise_kb_service.index_file(req.file_path, req.tenant_id, current_user.user_id, req.doc_type, req.department, req.version, ChunkStrategy(req.chunk_strategy), req.chunk_size, req.chunk_overlap)
    return ApiResponse[dict](data={'message':res.message,'chunk_count':res.chunk_count,'document':asdict(res.document)})
@router.get('/enterprise-kb/documents', response_model=ApiResponse[list[dict]])
async def list_documents(tenant_id: str = 'tenant_001'):
    return ApiResponse[list[dict]](data=[asdict(d) for d in enterprise_kb_service.list_documents(tenant_id)])
@router.post('/enterprise-kb/chat', response_model=ApiResponse[dict])
async def chat(req: ChatApiRequest, current_user: CurrentUser = Depends(get_current_user)):
    res = enterprise_kb_service.chat(KnowledgeChatRequest(req.question, req.tenant_id, current_user.user_id, req.top_k, req.metadata_filter))
    return ApiResponse[dict](data={'query_id':res.query_id,'question':res.question,'answer':res.answer,'sources':[asdict(s) for s in res.sources],'fallback_reason':res.fallback_reason,'debug':res.debug})
@router.get('/enterprise-kb/query-logs', response_model=ApiResponse[list[dict]])
async def list_logs(tenant_id: str = 'tenant_001', limit: int = 20): return ApiResponse[list[dict]](data=[asdict(x) for x in enterprise_kb_service.list_query_logs(tenant_id, limit)])
@router.post('/enterprise-kb/feedback', response_model=ApiResponse[dict])
async def submit_feedback(req: FeedbackApiRequest, current_user: CurrentUser = Depends(get_current_user)):
    return ApiResponse[dict](data=asdict(enterprise_kb_service.submit_feedback(req.query_id, req.tenant_id, current_user.user_id, FeedbackRating(req.rating), req.comment)))
@router.get('/enterprise-kb/feedbacks', response_model=ApiResponse[list[dict]])
async def feedbacks(tenant_id: str = 'tenant_001', limit: int = 20): return ApiResponse[list[dict]](data=[asdict(x) for x in enterprise_kb_service.list_feedbacks(tenant_id, limit)])
@router.get('/enterprise-kb/stats', response_model=ApiResponse[dict])
async def stats(tenant_id: str = 'tenant_001'): return ApiResponse[dict](data=asdict(enterprise_kb_service.get_stats(tenant_id)))
@router.post('/enterprise-kb/evaluation', response_model=ApiResponse[dict])
async def eval_report(): return ApiResponse[dict](data=enterprise_kb_service.run_evaluation())
