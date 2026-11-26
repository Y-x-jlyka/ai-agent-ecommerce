from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from app.langchain_rag.embeddings import create_embeddings


# 用文件自身位置锚定项目根，避免受运行时工作目录影响
CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma_langchain_rag"
COLLECTION_NAME = "ai_agent_course_kb"

# 创建向量存储
def create_vector_store() -> Chroma:
    embeddings = create_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

# 重建向量存储
def rebuild_vector_store(
    chunks: list[Document],
) -> Chroma:
    # 防护：chunks 为空时 Chroma 会报误导性的 "Expected Embeddings...got []"，
    # 提前拦截并说明真实原因（文档没加载到）
    if not chunks:
        raise ValueError(
            "chunks 为空：知识库没有加载到任何文档，"
            f"请检查目录是否存在且有 .md 文件：{CHROMA_DIR.parent / 'knowledge_base'}"
        )

    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)

    vector_store = create_vector_store()

    ids = [
        chunk.metadata.get("chunk_id", f"chunk_{index}")
        for index, chunk in enumerate(chunks)
    ]

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    return vector_store

# 相似度搜索
def similarity_search(
    query: str,
    k: int = 4,
) -> list[Document]:
    vector_store = create_vector_store()

    return vector_store.similarity_search(
        query=query,
        k=k,
    )