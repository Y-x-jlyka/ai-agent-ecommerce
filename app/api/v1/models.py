from fastapi import APIRouter

from app.core.config import settings
from app.schemas.response import ApiResponse

router = APIRouter()#模型列表路由：对外暴露支持的模型与厂商信息

@router.get("/models", response_model=ApiResponse[list[dict]])
# 查询支持的模型列表：按模型名前缀推断厂商，并标注是否支持流式与工具调用
async def list_models() -> ApiResponse[list[dict]]:
    models = []

    for model_name in settings.supported_models.split(","):
        model_name = model_name.strip()

        if not model_name:
            continue

        if model_name.startswith("deepseek"):
            provider = "deepseek"
        elif model_name.startswith("qwen"):
            provider = "qwen"
        elif model_name.startswith("gpt"):
            provider = "openai"
        else:
            provider = "unknown"

        models.append(
            {
                "model": model_name,
                "provider": provider,
                "support_stream": True,
                "support_tools": provider in ["deepseek", "qwen", "openai"],
            }
        )

    return ApiResponse[list[dict]](
        data=models
    )
