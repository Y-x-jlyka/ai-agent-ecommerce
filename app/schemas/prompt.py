from typing import Literal

from pydantic import BaseModel, Field


class IntentClassificationResult(BaseModel):#用户意图校验
    intent: Literal[
        "query_order",#查询订单
        "refund",#退款售后
        "product_question",#商品咨询
        "other",#其他
        "refund",
        "product_question",
        "other",
    ] = Field(..., description="用户意图")

    confidence: float = Field(..., ge=0, le=1, description="置信度")