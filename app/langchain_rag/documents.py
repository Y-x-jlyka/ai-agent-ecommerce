from pathlib import Path

from langchain_core.documents import Document


# 用文件自身位置锚定项目根（app/langchain_rag/ 向上两级），避免受运行时工作目录影响
KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"

# 加载markdown文件
def load_markdown_documents(
    base_dir: Path = KNOWLEDGE_BASE_DIR,
) -> list[Document]:
    documents: list[Document] = []

    for file_path in sorted(base_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")

        document_id = file_path.stem

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "document_id": document_id,
                    "file_type": "markdown",
                },
            )
        )

    return documents

# 打印文档信息
def print_documents(documents: list[Document]):
    for index, doc in enumerate(documents, start=1):
        print(f"Document {index}")
        print("metadata:", doc.metadata)
        print("content preview:", doc.page_content[:120])
        print("=" * 80)