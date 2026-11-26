import json
from typing import Any, Optional

# 按 SSE 协议格式化数据
def format_sse(
    data: Any,
    event: Optional[str] = None,
    event_id: Optional[str] = None,
    retry: Optional[int] = None,
) -> str:
    lines = []

    if event_id is not None:
        lines.append(f"id: {event_id}")

    if event is not None:
        lines.append(f"event: {event}")

    if retry is not None:
        lines.append(f"retry: {retry}")

    if isinstance(data, str):
        payload = data
    else:
        payload = json.dumps(data, ensure_ascii=False)

    for line in payload.splitlines():
        lines.append(f"data: {line}")

    return "\n".join(lines) + "\n\n"

# 生成流式输出结束事件
def format_done_event(data: Optional[dict] = None) -> str:
    return format_sse(
        event="done",
        data=data or {
            "finish_reason": "stop"
        },
    )

# 生成标准错误事件
def format_error_event(
    message: str,
    code: int = 50000,
    detail: Optional[dict] = None,
) -> str:

    return format_sse(
        event="error",
        data={
            "code": code,
            "message": message,
            "detail": detail or {},
        },
    )