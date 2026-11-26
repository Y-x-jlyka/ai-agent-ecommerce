from dataclasses import asdict
from typing import Literal
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.dependencies.auth import get_current_user
from app.rag_core import ChunkConfig, ChunkStrategy, document_parsing_service, document_chunking_service
from app.schemas.response import ApiResponse
from app.schemas.user import CurrentUser
router = APIRouter()
class ChunkFileRequest(BaseModel):
    file_path: str = Field(..., min_length=1)
    tenant_id: str = 'tenant_001'
    strategy: Literal['fixed_size','paragraph','page','element','heading','table_aware','code_aware'] = 'paragraph'
    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=80, ge=0)
    min_chunk_size: int = Field(default=30, ge=0)
@router.post('/documents/chunk', response_model=ApiResponse[dict])
async def chunk_document(req: ChunkFileRequest, current_user: CurrentUser = Depends(get_current_user)):
    doc = document_parsing_service.parse_file(req.file_path, req.tenant_id, current_user.user_id)
    res = document_chunking_service.split_document(doc, ChunkConfig(ChunkStrategy(req.strategy), req.chunk_size, req.chunk_overlap, req.min_chunk_size))
    return ApiResponse[dict](data=asdict(res))
