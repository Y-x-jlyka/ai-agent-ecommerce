from pydantic import BaseModel

# 构建 JSON 对象响应格式
def build_json_object_response_format() -> dict:
    return {
        "type": "json_object",
    }

# 构建 JSON 模式响应格式
def build_json_schema_response_format(
    schema: type[BaseModel],
    name: str,
    strict: bool = True,
) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": strict,
            "schema": schema.model_json_schema(),
        },
    }