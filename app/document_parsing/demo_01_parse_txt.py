from pathlib import Path

from app.document_parsing.service import document_parsing_service


# 用文件自身位置锚定项目根（scripts/ 向上两级），避免受运行时工作目录影响
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main():
    result = document_parsing_service.parse_file(
        str(PROJECT_ROOT / "data" / "sample_docs" / "after_sales.txt"),
        tenant_id="tenant_001",
        created_by="u_10001",
    )

    print("status:", result.status)
    print("title:", result.title)
    print("file_type:", result.file_type)

    if result.errors:
        print("errors:", result.errors)

    print("=" * 80)
    print("text:")
    print(result.text)

    print("=" * 80)
    print("elements:")
    for element in result.elements:
        print(element)


if __name__ == "__main__":
    main()
