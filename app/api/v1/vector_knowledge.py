from dataclasses import asdict
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.dependencies.auth import get_current_user
from app.rag_core import ChunkStrategy, VectorSearchRequest, vector_knowledge_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
router = APIRouter()
class IndexFileRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = 'tenant_001'
    chunk_strategy: str = 'heading'
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)
class SearchKnowledgeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    metadata_filter: dict[str, Any] | None = None
@router.post('/knowledge/index-file', response_model=ApiResponse[dict])
async def index_file(req: IndexFileRequest, current_user: CurrentUser = Depends(get_current_user)):
    res = vector_knowledge_service.index_file(req.file_path, req.tenant_id, current_user.user_id, ChunkStrategy(req.chunk_strategy), req.chunk_size, req.chunk_overlap)
    return ApiResponse[dict](data=asdict(res))
@router.post('/knowledge/search', response_model=ApiResponse[dict])
async def search_knowledge(req: SearchKnowledgeRequest):
    return ApiResponse[dict](data=asdict(vector_knowledge_service.search(VectorSearchRequest(req.query, req.top_k, req.metadata_filter))))
