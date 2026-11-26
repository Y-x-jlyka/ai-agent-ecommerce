from enum import Enum
# 运行环境枚举（开发/测试/预发/生产）
class AppEnv(str,Enum):
    DEVELOPMENT="development"
    TESTING="testing"
    STAGING="staging"
    PRODUCTION="production"
# Swagger 文档中的接口分组标签
class ApiTag:
    HEALTH="health"
    CHAT="chat"
    CONVERSATIONS="conversations"
    MODELS="models"
    RAG="rag"
    AGENTS="Agents"
