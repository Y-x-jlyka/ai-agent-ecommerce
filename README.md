# AI Agent 电商客服系统

基于 **LangChain 1.x + LangGraph 1.x** 从零构建的电商客服 AI 系统，覆盖模型接入、工具调用、RAG 检索、多轮记忆、会话持久化、人工审核（HITL）、多智能体协作与文档解析的完整链路。FastAPI 对外提供 REST API，所有能力均可通过 HTTP 调用。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 服务框架 | FastAPI + Uvicorn（异步、中间件链、统一响应/异常模型） |
| LLM 编排 | LangChain 1.3 / LangGraph 1.2 / langchain-openai（DeepSeek） |
| RAG | Chroma（向量库）+ 自研解析/分块管道 |
| 状态与存储 | LangGraph Checkpointer（内存 / SQLite / PostgreSQL）、LangGraph Store（长期记忆） |
| 基础设施 | Redis（缓存/会话）、PostgreSQL 16、Docker Compose |

## 项目导航

`app/` 按学习主题划分为 26 个模块，每个模块自带可独立运行的 demo（`demo_*.py`）与脚本（`scripts/test_*.py`）。

### LangChain 核心（模型 → 提示词 → 工具 → Agent）

| 模块 | 内容 |
| --- | --- |
| `app/langchain_demo` | 最小可运行示例：LLM 调用与消息模型 |
| `app/langchain_models` | 模型工厂：统一封装 DeepSeek/Qwen，超时与重试策略 |
| `app/langchain_prompts` | PromptTemplate / 少样本提示 / 消息占位符 |
| `app/langchain_structured_outputs` | Pydantic Schema 约束模型输出，字段级校验 |
| `app/langchain_tools` | StructuredTool 注册表：订单 / 物流 / 转人工查询 |
| `app/langchain_agents` | `create_agent` 工具调用 Agent（含异步流式输出） |
| `app/langchain_arch` | Agent 架构模式对比与选型 |

### RAG（检索增强生成）

| 模块 | 内容 |
| --- | --- |
| `app/rag_principles` | **手写 mini RAG**：零依赖实现切分/向量化/检索/生成五件套（→ 独立仓库 rag-from-scratch） |
| `app/langchain_rag` | 生产版：Chroma 向量库 + 知识库工具，供 Agent 检索调用 |
| `app/langchain_agent_rag` | Agent + RAG 复合：模型自主决定「查订单」还是「查知识库」 |

### 文档处理

| 模块 | 内容 |
| --- | --- |
| `app/document_parsing` | 统一解析管道：TXT / Markdown / HTML / DOCX / PDF，解析器工厂 + 结果状态机 |
| `app/document_chunking` | 多策略分块：固定长度 / 递归 / 按标题结构 |

### LangGraph（状态机、记忆与多智能体）

| 模块 | 内容 |
| --- | --- |
| `app/langgraph_intro` / `state` / `node_edge` | 状态定义、节点与边、条件路由 |
| `app/langgraph_core` | 核心模式：纯规则电商客服图（确定性路径 vs Agent 自主规划） |
| `app/langgraph_routing` / `memory` | 路由模式；短期记忆（messages）与长期记忆（Store） |
| `app/langgraph_persistence` | Checkpointer 持久化：跨请求恢复对话状态 |
| `app/langgraph_hitl` | Human-in-the-loop：`interrupt()` 暂停 / `Command(resume=)` 恢复 |
| `app/langgraph_ecommerce_agent` | **综合实战**：大额退款人工审核流（→ 独立仓库 langgraph-hitl-refund） |
| `app/langgraph_multi_agent` | 多智能体：监督者模式 / 手递手协作 |
| `app/deepagents_intro` / `deepagents_core` | DeepAgents 深度智能体模式 |

### 主应用骨架

`app/api`（25 个路由文件）、`core`（配置/日志/异常/中间件）、`db`、`models`、`schemas`、`services`、`repositories`、`redis`、`dependencies`（API Key 鉴权、租户上下文）——所有课程能力均通过 `app/api/v1/` 暴露为 REST 接口。

## 快速开始

```bash
# 1. 安装依赖（Python 3.12）
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 启动基础设施（PostgreSQL + Redis）
docker compose up -d

# 3. 配置环境变量（DeepSeek API Key 等）
cp .env.example .env   # 填入 DEEPSEEK_API_KEY

# 4. 启动服务
uvicorn app.main:app --reload --port 8000

# 5. 调用示例：HITL 退款审核
curl -X POST http://127.0.0.1:8000/api/v1/langgraph/ecommerce-agent/chat \
  -H "x-api-key: dev-api-key-123" -H "x-user-id: u_10001" -H "x-username: dawei" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "conv_001", "question": "我的订单 10003 申请退款。"}'
# → 大额退款触发人工审核，图在 human_review 节点前暂停
```

## 设计决策与踩坑实录

- **同步入口 + async-only 工具 = `NotImplementedError`**：混用 `StructuredTool(coroutine=...)` 时，Agent 入口必须统一走 `ainvoke`/`astream`
- **thread_id 三元组**：`tenant:user:conversation`，任何一段变化即新线程——resume 找不到断点时 LangGraph 会从头重跑图而非报错
- **LangGraph 状态按需写入**：提前终止的路径不会生成 TypedDict 中未写入的字段，API 层须防御式读取
- **相对路径陷阱**：`Path(__file__).resolve().parents[2]` 锚定项目根，杜绝「换个目录运行就找不到文件」
- **CWD 与 PyCharm 运行配置**：工作目录不一致导致的解析失败 / 空 embeddings，全项目已通过路径锚定根治

## License

MIT
