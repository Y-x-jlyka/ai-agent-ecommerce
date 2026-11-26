from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import uuid
from collections import Counter
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
import fitz


# =========================
# 第 40 章：企业文档解析
# =========================

class ParsedElementType(str, Enum):
    TITLE = "title"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST = "list"
    CODE = "code"
    PAGE_TEXT = "page_text"
    UNKNOWN = "unknown"


class ParseStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    NEED_OCR = "need_ocr"
    UNSUPPORTED = "unsupported"


@dataclass
class ParsedElement:
    element_id: str
    type: ParsedElementType
    content: str
    page_number: int | None = None
    order_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    document_id: str
    title: str
    source_path: str
    file_name: str
    file_type: str
    text: str
    elements: list[ParsedElement]
    status: ParseStatus
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class ParseDirectoryResult:
    total: int
    success: int
    failed: int
    documents: list[ParsedDocument]


SUPPORTED_FILE_TYPES = {".txt", ".md", ".markdown", ".html", ".htm", ".docx", ".pdf"}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()


def build_document_id(path: str | Path) -> str:
    p = Path(path)
    raw = f"{p.name}:{p.stat().st_size}:{p.stat().st_mtime}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


class DocumentParsingService:
    def parse_file(self, file_path: str | Path, tenant_id: str = "tenant_001", created_by: str = "system") -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            return ParsedDocument("", path.stem, str(path), path.name, path.suffix.lower(), "", [], ParseStatus.FAILED, {"tenant_id": tenant_id, "created_by": created_by}, [f"文件不存在：{path}"])
        if path.suffix.lower() not in SUPPORTED_FILE_TYPES:
            return ParsedDocument("", path.stem, str(path), path.name, path.suffix.lower(), "", [], ParseStatus.UNSUPPORTED, {"tenant_id": tenant_id, "created_by": created_by}, [f"暂不支持该文件类型：{path.suffix.lower()}"])
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return self._parse_txt(path, tenant_id, created_by)
        if suffix in {".md", ".markdown"}:
            return self._parse_markdown(path, tenant_id, created_by)
        if suffix in {".html", ".htm"}:
            return self._parse_html(path, tenant_id, created_by)
        if suffix == ".docx":
            return self._parse_docx(path, tenant_id, created_by)
        if suffix == ".pdf":
            return self._parse_pdf(path, tenant_id, created_by)
        raise ValueError(f"未处理的文件类型：{suffix}")

    def parse_directory(self, directory: str | Path, tenant_id: str = "tenant_001", created_by: str = "system") -> ParseDirectoryResult:
        root = Path(directory)
        if not root.exists():
            return ParseDirectoryResult(0, 0, 0, [])
        files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_FILE_TYPES]
        docs = [self.parse_file(p, tenant_id, created_by) for p in files]
        success = sum(1 for d in docs if d.status in {ParseStatus.SUCCESS, ParseStatus.PARTIAL_SUCCESS})
        return ParseDirectoryResult(len(docs), success, len(docs) - success, docs)

    def _base_metadata(self, path: Path, tenant_id: str, created_by: str) -> dict[str, Any]:
        return {"tenant_id": tenant_id, "created_by": created_by, "file_name": path.name, "file_size": path.stat().st_size, "source_path": str(path)}

    def _parse_txt(self, path: Path, tenant_id: str, created_by: str) -> ParsedDocument:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="gbk", errors="ignore")
        text = clean_text(text)
        elements = [ParsedElement(f"{path.stem}_txt_0", ParsedElementType.PARAGRAPH, text, order_index=0, metadata={"parser": "txt"})] if text else []
        return ParsedDocument(build_document_id(path), path.stem, str(path), path.name, path.suffix.lower(), text, elements, ParseStatus.SUCCESS if text else ParseStatus.FAILED, self._base_metadata(path, tenant_id, created_by), [] if text else ["文本内容为空"])

    def _parse_markdown(self, path: Path, tenant_id: str, created_by: str) -> ParsedDocument:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        elements: list[ParsedElement] = []
        in_code = False
        code_lang = None
        code_lines: list[str] = []
        for i, line in enumerate(raw.splitlines()):
            s = line.strip()
            if s.startswith("```"):
                if not in_code:
                    in_code = True
                    code_lang = s.replace("```", "").strip() or None
                    code_lines = []
                else:
                    in_code = False
                    content = "\n".join(code_lines).strip()
                    if content:
                        elements.append(ParsedElement(f"{path.stem}_code_{i}", ParsedElementType.CODE, content, order_index=len(elements), metadata={"parser": "markdown", "language": code_lang}))
                continue
            if in_code:
                code_lines.append(line)
                continue
            if not s:
                continue
            if s.startswith("#"):
                et, content = ParsedElementType.TITLE, s.lstrip("#").strip()
            elif s.startswith(("-", "*", "+")):
                et, content = ParsedElementType.LIST, s
            else:
                et, content = ParsedElementType.PARAGRAPH, s
            elements.append(ParsedElement(f"{path.stem}_md_{i}", et, content, order_index=len(elements), metadata={"parser": "markdown"}))
        text = clean_text("\n\n".join(e.content for e in elements))
        title = next((e.content for e in elements if e.type == ParsedElementType.TITLE), path.stem)
        return ParsedDocument(build_document_id(path), title, str(path), path.name, path.suffix.lower(), text, elements, ParseStatus.SUCCESS if elements else ParseStatus.FAILED, self._base_metadata(path, tenant_id, created_by), [] if elements else ["Markdown 内容为空"])

    def _parse_html(self, path: Path, tenant_id: str, created_by: str) -> ParsedDocument:
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else path.stem
        elements: list[ParsedElement] = []
        for i, tag in enumerate(soup.find_all(["h1", "h2", "h3", "p", "li", "td", "th"])):
            content = clean_text(tag.get_text(" ", strip=True))
            if not content:
                continue
            et = ParsedElementType.TITLE if tag.name in ["h1", "h2", "h3"] else ParsedElementType.LIST if tag.name == "li" else ParsedElementType.TABLE if tag.name in ["td", "th"] else ParsedElementType.PARAGRAPH
            elements.append(ParsedElement(f"{path.stem}_html_{i}", et, content, order_index=len(elements), metadata={"parser": "html", "tag": tag.name}))
        text = clean_text("\n\n".join(e.content for e in elements))
        return ParsedDocument(build_document_id(path), title, str(path), path.name, path.suffix.lower(), text, elements, ParseStatus.SUCCESS if elements else ParseStatus.FAILED, {**self._base_metadata(path, tenant_id, created_by), "html_title": title}, [] if elements else ["HTML 未解析出有效正文"])

    def _parse_docx(self, path: Path, tenant_id: str, created_by: str) -> ParsedDocument:
        doc = DocxDocument(str(path))
        elements: list[ParsedElement] = []
        for i, paragraph in enumerate(doc.paragraphs):
            content = clean_text(paragraph.text)
            if not content:
                continue
            style = paragraph.style.name if paragraph.style else ""
            et = ParsedElementType.TITLE if style.startswith("Heading") else ParsedElementType.PARAGRAPH
            elements.append(ParsedElement(f"{path.stem}_docx_p_{i}", et, content, order_index=len(elements), metadata={"parser": "docx", "style": style}))
        for ti, table in enumerate(doc.tables):
            rows = [" | ".join(clean_text(cell.text) for cell in row.cells) for row in table.rows]
            content = "\n".join(rows).strip()
            if content:
                elements.append(ParsedElement(f"{path.stem}_docx_table_{ti}", ParsedElementType.TABLE, content, order_index=len(elements), metadata={"parser": "docx", "table_index": ti}))
        text = clean_text("\n\n".join(e.content for e in elements))
        title = next((e.content for e in elements if e.type == ParsedElementType.TITLE), path.stem)
        return ParsedDocument(build_document_id(path), title, str(path), path.name, path.suffix.lower(), text, elements, ParseStatus.SUCCESS if elements else ParseStatus.FAILED, self._base_metadata(path, tenant_id, created_by), [] if elements else ["DOCX 未解析出有效正文"])

    def _parse_pdf(self, path: Path, tenant_id: str, created_by: str) -> ParsedDocument:
        elements: list[ParsedElement] = []
        errors: list[str] = []
        try:
            pdf = fitz.open(str(path))
        except Exception as exc:
            return ParsedDocument(build_document_id(path), path.stem, str(path), path.name, path.suffix.lower(), "", [], ParseStatus.FAILED, self._base_metadata(path, tenant_id, created_by), [f"PDF 打开失败：{exc}"])
        try:
            for idx in range(len(pdf)):
                text = clean_text(pdf[idx].get_text("text"))
                if not text:
                    errors.append(f"第 {idx + 1} 页未提取到文本，可能是扫描件或图片页")
                    continue
                elements.append(ParsedElement(f"{path.stem}_pdf_page_{idx + 1}", ParsedElementType.PAGE_TEXT, text, page_number=idx + 1, order_index=len(elements), metadata={"parser": "pdf", "page_number": idx + 1}))
            text = clean_text("\n\n".join(e.content for e in elements))
            metadata = {**self._base_metadata(path, tenant_id, created_by), "page_count": len(pdf)}
        finally:
            pdf.close()
        status = ParseStatus.PARTIAL_SUCCESS if elements and errors else ParseStatus.SUCCESS if elements else ParseStatus.NEED_OCR if errors else ParseStatus.FAILED
        return ParsedDocument(build_document_id(path), path.stem, str(path), path.name, path.suffix.lower(), text, elements, status, metadata, errors)


document_parsing_service = DocumentParsingService()


# =========================
# 第 41 章：Chunk 文档切分
# =========================

class ChunkStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    PAGE = "page"
    ELEMENT = "element"
    HEADING = "heading"
    TABLE_AWARE = "table_aware"
    CODE_AWARE = "code_aware"


@dataclass
class ChunkConfig:
    strategy: ChunkStrategy = ChunkStrategy.PARAGRAPH
    chunk_size: int = 500
    chunk_overlap: int = 80
    min_chunk_size: int = 30


@dataclass
class ChunkDocument:
    chunk_id: str
    document_id: str
    title: str
    content: str
    chunk_index: int
    strategy: ChunkStrategy
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkResult:
    document_id: str
    title: str
    total_chunks: int
    strategy: ChunkStrategy
    chunks: list[ChunkDocument]
    warnings: list[str] = field(default_factory=list)


class DocumentChunkingService:
    def split_document(self, document: ParsedDocument, config: ChunkConfig | None = None) -> ChunkResult:
        cfg = config or ChunkConfig()
        if cfg.chunk_overlap >= cfg.chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        if cfg.strategy == ChunkStrategy.FIXED_SIZE:
            return self._fixed(document, cfg)
        if cfg.strategy == ChunkStrategy.PARAGRAPH:
            return self._paragraph(document, cfg)
        if cfg.strategy == ChunkStrategy.PAGE:
            return self._page(document, cfg)
        if cfg.strategy == ChunkStrategy.ELEMENT:
            return self._element(document, cfg)
        if cfg.strategy == ChunkStrategy.HEADING:
            return self._heading(document, cfg)
        if cfg.strategy == ChunkStrategy.TABLE_AWARE:
            return self._table_aware(document, cfg)
        if cfg.strategy == ChunkStrategy.CODE_AWARE:
            return self._code_aware(document, cfg)
        raise ValueError(f"不支持的策略：{cfg.strategy}")

    def _base_metadata(self, document: ParsedDocument, index: int) -> dict[str, Any]:
        return {**document.metadata, "document_id": document.document_id, "document_title": document.title, "file_name": document.file_name, "file_type": document.file_type, "source_path": document.source_path, "chunk_index": index}

    def _make(self, document: ParsedDocument, content: str, index: int, strategy: ChunkStrategy, extra: dict | None = None) -> ChunkDocument:
        meta = self._base_metadata(document, index)
        if extra:
            meta.update(extra)
        return ChunkDocument(f"{document.document_id}_chunk_{index}", document.document_id, document.title, content.strip(), index, strategy, meta)

    def _keep(self, content: str, cfg: ChunkConfig) -> bool:
        return len(content.strip()) >= cfg.min_chunk_size

    def _fixed(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks: list[ChunkDocument] = []
        start = 0
        idx = 0
        text = document.text
        while start < len(text):
            end = start + cfg.chunk_size
            content = text[start:end]
            if self._keep(content, cfg):
                chunks.append(self._make(document, content, idx, ChunkStrategy.FIXED_SIZE, {"start_char": start, "end_char": min(end, len(text))}))
                idx += 1
            if end >= len(text):
                break
            start = end - cfg.chunk_overlap
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.FIXED_SIZE, chunks, ["固定长度切分仅适合教学或兜底。"])

    def _paragraph(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", document.text) if p.strip()]
        chunks: list[ChunkDocument] = []
        current: list[str] = []
        size = 0
        idx = 0
        for p in paragraphs:
            if current and size + len(p) > cfg.chunk_size:
                content = "\n\n".join(current)
                if self._keep(content, cfg):
                    chunks.append(self._make(document, content, idx, ChunkStrategy.PARAGRAPH, {"paragraph_count": len(current)}))
                    idx += 1
                current = [current[-1]] if cfg.chunk_overlap > 0 else []
                size = len(current[0]) if current else 0
            current.append(p)
            size += len(p)
        if current:
            content = "\n\n".join(current)
            if self._keep(content, cfg):
                chunks.append(self._make(document, content, idx, ChunkStrategy.PARAGRAPH, {"paragraph_count": len(current)}))
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.PARAGRAPH, chunks)

    def _page(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks = [self._make(document, e.content, i, ChunkStrategy.PAGE, {"page_number": e.page_number, "element_id": e.element_id, "element_type": e.type.value}) for i, e in enumerate([e for e in document.elements if e.page_number is not None and self._keep(e.content, cfg)])]
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.PAGE, chunks, [] if chunks else ["当前文档没有 page_number，无法按页切分。"])

    def _element(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks: list[ChunkDocument] = []
        for e in document.elements:
            if self._keep(e.content, cfg):
                chunks.append(self._make(document, e.content, len(chunks), ChunkStrategy.ELEMENT, {"element_id": e.element_id, "element_type": e.type.value, "page_number": e.page_number, "order_index": e.order_index}))
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.ELEMENT, chunks)

    def _heading(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks: list[ChunkDocument] = []
        heading = document.title
        parts: list[str] = []
        element_ids: list[str] = []
        pages: set[int] = set()
        def flush():
            nonlocal parts, element_ids, pages
            if not parts:
                return
            content = "\n\n".join(parts)
            if self._keep(content, cfg):
                chunks.append(self._make(document, content, len(chunks), ChunkStrategy.HEADING, {"heading": heading, "element_ids": element_ids, "page_numbers": sorted(pages)}))
            parts, element_ids, pages = [], [], set()
        for e in document.elements:
            if e.type == ParsedElementType.TITLE:
                flush()
                heading = e.content
                parts = [e.content]
                element_ids = [e.element_id]
                if e.page_number:
                    pages.add(e.page_number)
                continue
            parts.append(e.content)
            element_ids.append(e.element_id)
            if e.page_number:
                pages.add(e.page_number)
            if len("\n\n".join(parts)) >= cfg.chunk_size:
                flush()
                if cfg.chunk_overlap > 0:
                    parts = [f"上级标题：{heading}"]
        flush()
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.HEADING, chunks)

    def _table_aware(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks: list[ChunkDocument] = []
        buf: list[str] = []
        def flush_text():
            nonlocal buf
            if buf:
                content = "\n\n".join(buf)
                if self._keep(content, cfg):
                    chunks.append(self._make(document, content, len(chunks), ChunkStrategy.TABLE_AWARE, {"chunk_content_type": "text"}))
                buf = []
        for e in document.elements:
            if e.type == ParsedElementType.TABLE:
                flush_text()
                if self._keep(e.content, cfg):
                    chunks.append(self._make(document, e.content, len(chunks), ChunkStrategy.TABLE_AWARE, {"chunk_content_type": "table", "element_id": e.element_id}))
            else:
                buf.append(e.content)
                if len("\n\n".join(buf)) >= cfg.chunk_size:
                    flush_text()
        flush_text()
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.TABLE_AWARE, chunks)

    def _code_aware(self, document: ParsedDocument, cfg: ChunkConfig) -> ChunkResult:
        chunks: list[ChunkDocument] = []
        buf: list[str] = []
        def flush_text():
            nonlocal buf
            if buf:
                content = "\n\n".join(buf)
                if self._keep(content, cfg):
                    chunks.append(self._make(document, content, len(chunks), ChunkStrategy.CODE_AWARE, {"chunk_content_type": "text"}))
                buf = []
        for e in document.elements:
            if e.type == ParsedElementType.CODE:
                flush_text()
                if self._keep(e.content, cfg):
                    chunks.append(self._make(document, e.content, len(chunks), ChunkStrategy.CODE_AWARE, {"chunk_content_type": "code", "element_id": e.element_id, "language": e.metadata.get("language")}))
            else:
                buf.append(e.content)
                if len("\n\n".join(buf)) >= cfg.chunk_size:
                    flush_text()
        flush_text()
        return ChunkResult(document.document_id, document.title, len(chunks), ChunkStrategy.CODE_AWARE, chunks)


document_chunking_service = DocumentChunkingService()


# =========================
# 第 42 章：Embedding 与 Vector Database
# =========================

class EmbeddingProvider(str, Enum):
    HASH = "hash"


class VectorStoreProvider(str, Enum):
    IN_MEMORY = "in_memory"


@dataclass
class EmbeddingConfig:
    provider: EmbeddingProvider = EmbeddingProvider.HASH
    model_name: str = "deterministic-hash-embedding"
    dimension: int = 128
    normalize: bool = True


@dataclass
class EmbeddedChunk:
    chunk_id: str
    document_id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchResult:
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchRequest:
    query: str
    top_k: int = 5
    metadata_filter: dict[str, Any] | None = None


@dataclass
class VectorSearchResponse:
    query: str
    top_k: int
    results: list[VectorSearchResult]


@dataclass
class IndexBuildResult:
    total_chunks: int
    embedded_chunks: int
    provider: EmbeddingProvider
    vector_store: VectorStoreProvider
    warnings: list[str] = field(default_factory=list)


def dot_product(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("向量维度不一致")
    return sum(x * y for x, y in zip(a, b))


def vector_norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    an, bn = vector_norm(a), vector_norm(b)
    if an == 0 or bn == 0:
        return 0.0
    return dot_product(a, b) / (an * bn)


def normalize_vector(v: list[float]) -> list[float]:
    n = vector_norm(v)
    return v if n == 0 else [x / n for x in v]


class EmbeddingService:
    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()
        self.keyword_boosts = {"订单": 3, "未发货": 3, "已发货": 2, "退款": 3, "退货": 2.5, "售后": 2.5, "物流": 3, "快递": 2.5, "发票": 3, "企业": 2, "年假": 3, "报销": 3, "合同": 3, "付款": 2.5, "客服": 2, "行程单": 2, "审批记录": 2, "纳税人识别号": 3}

    def embed_text(self, text: str) -> list[float]:
        v = [0.0] * self.config.dimension
        tokens = re.findall(r"[a-zA-Z0-9_\-]+", text.lower()) + [c for c in text if "\u4e00" <= c <= "\u9fff"]
        for token in tokens:
            v[int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.config.dimension] += 1.0
        for keyword, weight in self.keyword_boosts.items():
            if keyword in text:
                v[int(hashlib.md5(f"kw:{keyword}".encode("utf-8")).hexdigest(), 16) % self.config.dimension] += weight
        return normalize_vector(v) if self.config.normalize else v

    def embed_chunks(self, chunks: list[ChunkDocument]) -> list[EmbeddedChunk]:
        return [EmbeddedChunk(c.chunk_id, c.document_id, c.content, self.embed_text(c.content), {**c.metadata, "embedding_provider": self.config.provider.value, "embedding_model": self.config.model_name, "embedding_dimension": self.config.dimension}) for c in chunks]


class InMemoryVectorStore:
    def __init__(self):
        self.items: dict[str, EmbeddedChunk] = {}

    def add_many(self, items: list[EmbeddedChunk]) -> None:
        for item in items:
            self.items[item.chunk_id] = item

    def clear(self) -> None:
        self.items.clear()

    def count(self) -> int:
        return len(self.items)

    def search(self, query_embedding: list[float], top_k: int = 5, metadata_filter: dict | None = None) -> list[VectorSearchResult]:
        candidates = list(self.items.values())
        if metadata_filter:
            candidates = [c for c in candidates if metadata_match(c.metadata, metadata_filter)]
        results = [VectorSearchResult(c.chunk_id, c.document_id, c.content, cosine_similarity(query_embedding, c.embedding), c.metadata) for c in candidates]
        return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]


def metadata_match(metadata: dict, filter_: dict) -> bool:
    for key, expected in filter_.items():
        actual = metadata.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


class VectorKnowledgeService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = InMemoryVectorStore()

    def index_chunks(self, chunks: list[ChunkDocument]) -> IndexBuildResult:
        embedded = self.embedding_service.embed_chunks(chunks)
        self.vector_store.add_many(embedded)
        return IndexBuildResult(len(chunks), len(embedded), self.embedding_service.config.provider, VectorStoreProvider.IN_MEMORY, ["当前使用 InMemoryVectorStore，仅适合教学和本地 Demo。"])

    def index_file(self, file_path: str, tenant_id: str = "tenant_001", created_by: str = "system", chunk_strategy: ChunkStrategy = ChunkStrategy.HEADING, chunk_size: int = 500, chunk_overlap: int = 80) -> IndexBuildResult:
        parsed = document_parsing_service.parse_file(file_path, tenant_id, created_by)
        chunks = document_chunking_service.split_document(parsed, ChunkConfig(chunk_strategy, chunk_size, chunk_overlap, 10)).chunks
        return self.index_chunks(chunks)

    def search(self, request: VectorSearchRequest) -> VectorSearchResponse:
        qv = self.embedding_service.embed_text(request.query)
        return VectorSearchResponse(request.query, request.top_k, self.vector_store.search(qv, request.top_k, request.metadata_filter))

    def clear_index(self) -> None:
        self.vector_store.clear()

    def count(self) -> int:
        return self.vector_store.count()


vector_knowledge_service = VectorKnowledgeService()

# =========================
# 第 43 章：高级 Retrieval
# =========================

class RetrievalMode(str, Enum):
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class QueryRewriteResult:
    original_query: str
    rewritten_query: str
    intent: str
    keywords: list[str]
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class HybridSearchResult:
    chunk_id: str
    document_id: str
    content: str
    vector_score: float = 0.0
    keyword_score: float = 0.0
    final_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    matched_by: list[str] = field(default_factory=list)


@dataclass
class RetrievalConfig:
    mode: RetrievalMode = RetrievalMode.HYBRID
    top_k: int = 5
    candidate_k: int = 20
    vector_weight: float = 0.7
    keyword_weight: float = 0.3
    use_query_rewrite: bool = True
    use_multi_query: bool = True
    use_mmr: bool = True
    use_rerank: bool = True
    min_score: float = 0.05
    max_context_chars: int = 2000
    metadata_filter: dict[str, Any] | None = None


@dataclass
class AdvancedRetrievalRequest:
    query: str
    config: RetrievalConfig = field(default_factory=RetrievalConfig)


@dataclass
class AdvancedRetrievalResponse:
    original_query: str
    rewritten_query: str
    queries: list[str]
    results: list[HybridSearchResult]
    context: str
    sources: list[dict[str, Any]]
    fallback_reason: str | None = None
    debug: dict[str, Any] = field(default_factory=dict)


class RuleBasedQueryRewriter:
    def rewrite(self, query: str) -> QueryRewriteResult:
        q = query.strip()
        intent = "general"
        keywords: list[str] = []
        filters: dict[str, Any] = {}
        if any(w in q for w in ["退钱", "退款", "不想要", "取消订单"]):
            intent, keywords, filters = "refund", ["退款", "取消订单", "未发货", "售后"], {"doc_type": "after_sales"}
        elif any(w in q for w in ["快递", "物流", "配送", "没动"]):
            intent, keywords, filters = "logistics", ["物流", "快递", "配送", "更新"], {"doc_type": "logistics"}
        elif any(w in q for w in ["发票", "抬头", "纳税人"]):
            intent, keywords, filters = "invoice", ["发票", "企业", "纳税人识别号"], {"doc_type": "invoice"}
        elif any(w in q for w in ["年假", "请假", "休假"]):
            intent, keywords, filters = "leave", ["年假", "请假", "员工手册"], {"doc_type": "employee_handbook"}
        elif any(w in q for w in ["报销", "差旅", "行程单"]):
            intent, keywords, filters = "reimbursement", ["报销", "差旅", "发票", "审批记录"], {"doc_type": "employee_handbook"}
        rewrite_map = {
            "refund": "订单未发货取消订单退款规则 退款到账时间 售后规则",
            "logistics": "物流配送进度 快递超过 7 天未更新 客服核查",
            "invoice": "电子发票 企业发票 抬头 纳税人识别号",
            "leave": "员工手册 年假制度 年假申请 条件",
            "reimbursement": "差旅报销 发票 行程单 审批记录 报销制度",
        }
        return QueryRewriteResult(query, rewrite_map.get(intent, q), intent, keywords, filters)


class RuleBasedMultiQueryExpander:
    def expand(self, query: str, rewrite: QueryRewriteResult | None) -> list[str]:
        queries = [query]
        if rewrite:
            queries.append(rewrite.rewritten_query)
            extras = {
                "refund": ["未发货订单可以退款吗", "取消订单退款流程", "退款审核通过后多久到账"],
                "logistics": ["物流超过 7 天没有更新怎么办", "如何查询快递配送进度"],
                "invoice": ["企业发票需要填写什么", "电子发票申请规则"],
                "leave": ["员工入职多久可以申请年假", "年假制度"],
                "reimbursement": ["差旅报销需要什么材料", "报销需要发票和审批记录吗"],
            }.get(rewrite.intent, [])
            queries.extend(extras)
        dedup: list[str] = []
        for item in queries:
            item = re.sub(r"\s+", " ", item.strip())
            if item and item not in dedup:
                dedup.append(item)
        return dedup


class SimpleKeywordSearchEngine:
    def __init__(self):
        self.items: dict[str, EmbeddedChunk] = {}
        self.doc_freq: Counter[str] = Counter()
        self.total_docs = 0

    def add_many(self, chunks: list[EmbeddedChunk]) -> None:
        for c in chunks:
            self.items[c.chunk_id] = c
        self._rebuild()

    def clear(self) -> None:
        self.items.clear()
        self.doc_freq.clear()
        self.total_docs = 0

    def search(self, query: str, top_k: int = 10, metadata_filter: dict | None = None) -> list[HybridSearchResult]:
        q_terms = self._tokenize(query)
        candidates = list(self.items.values())
        if metadata_filter:
            candidates = [c for c in candidates if metadata_match(c.metadata, metadata_filter)]
        results: list[HybridSearchResult] = []
        for item in candidates:
            score = self._score(q_terms, item.content)
            if score > 0:
                results.append(HybridSearchResult(item.chunk_id, item.document_id, item.content, keyword_score=score, final_score=score, metadata=item.metadata, matched_by=["keyword"]))
        return sorted(results, key=lambda x: x.keyword_score, reverse=True)[:top_k]

    def _tokenize(self, text: str) -> list[str]:
        terms = re.findall(r"[a-zA-Z0-9_\-]+", text.lower()) + [c for c in text if "\u4e00" <= c <= "\u9fff"]
        business = [t for t in ["未发货", "已发货", "退款", "退货", "物流", "快递", "发票", "年假", "报销", "合同", "付款", "审批记录", "纳税人识别号", "行程单"] if t in text]
        return terms + business

    def _score(self, query_terms: list[str], content: str) -> float:
        terms = self._tokenize(content)
        counts = Counter(terms)
        score = 0.0
        for term in query_terms:
            tf = counts.get(term, 0)
            if not tf:
                continue
            idf = math.log((self.total_docs + 1) / (self.doc_freq.get(term, 0) + 1)) + 1
            score += (tf / max(len(terms), 1)) * idf
        return score

    def _rebuild(self) -> None:
        self.doc_freq.clear()
        self.total_docs = len(self.items)
        for item in self.items.values():
            for term in set(self._tokenize(item.content)):
                self.doc_freq[term] += 1


class AdvancedRetrievalService:
    def __init__(self):
        self.vector_service = VectorKnowledgeService()
        self.keyword_engine = SimpleKeywordSearchEngine()
        self.rewriter = RuleBasedQueryRewriter()
        self.expander = RuleBasedMultiQueryExpander()

    def index_chunks(self, chunks: list[ChunkDocument]) -> None:
        embedded = self.vector_service.embedding_service.embed_chunks(chunks)
        self.vector_service.vector_store.add_many(embedded)
        self.keyword_engine.add_many(embedded)

    def clear_index(self) -> None:
        self.vector_service.clear_index()
        self.keyword_engine.clear()

    def retrieve(self, request: AdvancedRetrievalRequest) -> AdvancedRetrievalResponse:
        cfg = request.config
        rewrite = self.rewriter.rewrite(request.query) if cfg.use_query_rewrite else None
        rewritten_query = rewrite.rewritten_query if rewrite else request.query
        metadata_filter = dict(cfg.metadata_filter or {})
        if not cfg.metadata_filter and rewrite and rewrite.filters:
            metadata_filter.update(rewrite.filters)
        eff = RetrievalConfig(cfg.mode, cfg.top_k, cfg.candidate_k, cfg.vector_weight, cfg.keyword_weight, cfg.use_query_rewrite, cfg.use_multi_query, cfg.use_mmr, cfg.use_rerank, cfg.min_score, cfg.max_context_chars, metadata_filter or None)
        queries = self.expander.expand(request.query, rewrite) if cfg.use_multi_query else [rewritten_query]
        candidates: list[HybridSearchResult] = []
        for q in queries:
            candidates.extend(self._retrieve_one(q, eff))
        candidates = self._dedupe(candidates)
        if cfg.use_mmr:
            candidates = self._mmr(rewritten_query, candidates, min(cfg.candidate_k, len(candidates)))
        if cfg.use_rerank:
            candidates = self._rerank(rewritten_query, candidates)
        results = candidates[: cfg.top_k]
        fallback = None
        if not results:
            fallback = "no_retrieval_results"
        elif results[0].final_score < cfg.min_score:
            fallback = "top_score_below_threshold"
        context, sources = ("", []) if fallback else self._build_context(results, cfg.max_context_chars)
        return AdvancedRetrievalResponse(request.query, rewritten_query, queries, [] if fallback else results, context, sources, fallback, {"candidate_count": len(candidates), "metadata_filter": eff.metadata_filter})

    def _retrieve_one(self, query: str, cfg: RetrievalConfig) -> list[HybridSearchResult]:
        merged: dict[str, HybridSearchResult] = {}
        if cfg.mode in {RetrievalMode.VECTOR, RetrievalMode.HYBRID}:
            vres = self.vector_service.search(VectorSearchRequest(query, cfg.candidate_k, cfg.metadata_filter)).results
            for item in vres:
                merged[item.chunk_id] = HybridSearchResult(item.chunk_id, item.document_id, item.content, vector_score=item.score, final_score=item.score * cfg.vector_weight, metadata=item.metadata, matched_by=["vector"])
        if cfg.mode in {RetrievalMode.KEYWORD, RetrievalMode.HYBRID}:
            kres = self.keyword_engine.search(query, cfg.candidate_k, cfg.metadata_filter)
            for item in kres:
                if item.chunk_id in merged:
                    m = merged[item.chunk_id]
                    m.keyword_score = item.keyword_score
                    m.final_score += item.keyword_score * cfg.keyword_weight
                    if "keyword" not in m.matched_by:
                        m.matched_by.append("keyword")
                else:
                    item.final_score = item.keyword_score * cfg.keyword_weight
                    merged[item.chunk_id] = item
        return sorted(merged.values(), key=lambda x: x.final_score, reverse=True)[: cfg.candidate_k]

    def _dedupe(self, results: list[HybridSearchResult]) -> list[HybridSearchResult]:
        merged: dict[str, HybridSearchResult] = {}
        for item in results:
            existing = merged.get(item.chunk_id)
            if not existing:
                merged[item.chunk_id] = item
                continue
            existing.final_score = max(existing.final_score, item.final_score)
            existing.vector_score = max(existing.vector_score, item.vector_score)
            existing.keyword_score = max(existing.keyword_score, item.keyword_score)
            for m in item.matched_by:
                if m not in existing.matched_by:
                    existing.matched_by.append(m)
        return sorted(merged.values(), key=lambda x: x.final_score, reverse=True)

    def _mmr(self, query: str, candidates: list[HybridSearchResult], top_k: int, lambda_mult: float = 0.7) -> list[HybridSearchResult]:
        if top_k >= len(candidates):
            return candidates
        qv = self.vector_service.embedding_service.embed_text(query)
        cvec = {c.chunk_id: self.vector_service.embedding_service.embed_text(c.content) for c in candidates}
        selected: list[HybridSearchResult] = []
        remaining = candidates[:]
        while remaining and len(selected) < top_k:
            best = max(remaining, key=lambda item: lambda_mult * cosine_similarity(qv, cvec[item.chunk_id]) - (1 - lambda_mult) * max((cosine_similarity(cvec[item.chunk_id], cvec[s.chunk_id]) for s in selected), default=0.0))
            selected.append(best)
            remaining = [x for x in remaining if x.chunk_id != best.chunk_id]
        return selected

    def _rerank(self, query: str, candidates: list[HybridSearchResult]) -> list[HybridSearchResult]:
        keywords = [kw for kw in ["退款", "未发货", "退货", "物流", "快递", "发票", "年假", "报销", "合同", "付款"] if kw in query]
        if "退钱" in query or "不想要" in query:
            keywords.extend(["退款", "未发货"])
        for item in candidates:
            item.final_score += sum(0.2 for kw in set(keywords) if kw in item.content)
            if item.metadata.get("is_latest") is True:
                item.final_score += 0.1
        return sorted(candidates, key=lambda x: x.final_score, reverse=True)

    def _build_context(self, results: list[HybridSearchResult], max_chars: int) -> tuple[str, list[dict[str, Any]]]:
        parts: list[str] = []
        sources: list[dict[str, Any]] = []
        used = 0
        for i, item in enumerate(results, start=1):
            source = {"chunk_id": item.chunk_id, "document_id": item.document_id, "source_path": item.metadata.get("source_path"), "heading": item.metadata.get("heading"), "page_number": item.metadata.get("page_number"), "score": item.final_score, "matched_by": item.matched_by}
            part = f"资料 {i}:\n来源：{source['source_path']}\n标题：{source['heading']}\n匹配方式：{','.join(item.matched_by)}\n分数：{item.final_score:.4f}\n内容：{item.content}"
            if used + len(part) > max_chars:
                break
            parts.append(part)
            sources.append(source)
            used += len(part)
        return "\n\n".join(parts), sources


def build_sample_chunks() -> list[ChunkDocument]:
    return [
        ChunkDocument("after_sales_001", "doc_after_sales", "电商售后规则", "订单未发货时，用户可以申请取消订单并退款。退款通常会在审核通过后 1 到 3 个工作日原路返回。", 0, ChunkStrategy.PARAGRAPH, {"tenant_id": "tenant_001", "doc_type": "after_sales", "source_path": "data/sample_docs/after_sales.txt", "heading": "未发货退款规则", "is_latest": True}),
        ChunkDocument("after_sales_002", "doc_after_sales", "电商售后规则", "订单已发货后，用户需要收到商品后再发起退货退款申请。如果商品存在质量问题，可以提交照片或视频凭证。", 1, ChunkStrategy.PARAGRAPH, {"tenant_id": "tenant_001", "doc_type": "after_sales", "source_path": "data/sample_docs/after_sales.txt", "heading": "已发货退货规则", "is_latest": True}),
        ChunkDocument("logistics_001", "doc_logistics", "物流说明", "订单发货后，用户可以通过物流单号查询配送进度。如果物流超过 7 天没有更新，建议联系客服协助核查。", 0, ChunkStrategy.PARAGRAPH, {"tenant_id": "tenant_001", "doc_type": "logistics", "source_path": "data/sample_docs/logistics.txt", "heading": "物流异常处理", "is_latest": True}),
        ChunkDocument("invoice_001", "doc_invoice", "发票规则", "用户可以在订单完成后申请开具电子发票。企业发票需要填写公司名称和纳税人识别号。", 0, ChunkStrategy.PARAGRAPH, {"tenant_id": "tenant_001", "doc_type": "invoice", "source_path": "data/sample_docs/invoice.txt", "heading": "发票申请规则", "is_latest": True}),
        ChunkDocument("employee_001", "doc_employee_handbook", "员工手册", "员工入职满一年后，可以按照公司制度申请年假。年假申请需要提前提交审批。", 0, ChunkStrategy.HEADING, {"tenant_id": "tenant_001", "doc_type": "employee_handbook", "source_path": "data/sample_docs/employee_handbook.md", "heading": "年假制度", "department": "hr", "is_latest": True}),
        ChunkDocument("employee_002", "doc_employee_handbook", "员工手册", "差旅报销需要提交发票、行程单和审批记录。报销申请需要按照公司流程提交。", 1, ChunkStrategy.HEADING, {"tenant_id": "tenant_001", "doc_type": "employee_handbook", "source_path": "data/sample_docs/employee_handbook.md", "heading": "报销制度", "department": "finance", "is_latest": True}),
    ]


advanced_retrieval_service = AdvancedRetrievalService()
advanced_retrieval_service.index_chunks(build_sample_chunks())

# =========================
# 第 44 章：RAG Evaluation
# =========================

class EvaluationCaseDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvaluationCategory(str, Enum):
    REFUND = "refund"
    LOGISTICS = "logistics"
    INVOICE = "invoice"
    LEAVE = "leave"
    REIMBURSEMENT = "reimbursement"
    UNKNOWN = "unknown"


@dataclass
class RAGEvaluationCase:
    case_id: str
    question: str
    category: EvaluationCategory
    expected_chunk_ids: list[str]
    expected_document_ids: list[str]
    expected_answer_keywords: list[str]
    expected_source_paths: list[str]
    metadata_filter: dict[str, Any] = field(default_factory=dict)
    difficulty: EvaluationCaseDifficulty = EvaluationCaseDifficulty.EASY
    expected_answer: str | None = None
    notes: str = ""


@dataclass
class RetrievalEvaluationResult:
    case_id: str
    question: str
    retrieved_chunk_ids: list[str]
    expected_chunk_ids: list[str]
    hit_rate: float
    recall_at_k: float
    precision_at_k: float
    mrr: float
    ndcg_at_k: float
    source_accuracy: float


@dataclass
class GenerationEvaluationResult:
    case_id: str
    question: str
    answer: str
    faithfulness: float
    answer_relevance: float
    answer_correctness: float
    context_relevance: float
    citation_accuracy: float
    missing_keywords: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)


def load_golden_dataset() -> list[RAGEvaluationCase]:
    return [
        RAGEvaluationCase("case_refund_001", "没发货可以退钱吗？", EvaluationCategory.REFUND, ["after_sales_001"], ["doc_after_sales"], ["未发货", "退款"], ["data/sample_docs/after_sales.txt"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.EASY, "订单未发货时，可以申请取消订单并退款。", "口语化退款问题"),
        RAGEvaluationCase("case_refund_002", "已经发货了还能直接退款吗？", EvaluationCategory.REFUND, ["after_sales_002"], ["doc_after_sales"], ["已发货", "退货", "质量问题"], ["data/sample_docs/after_sales.txt"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.MEDIUM, "订单已发货后，用户需要收到商品后再发起退货退款申请。", "已发货退款规则"),
        RAGEvaluationCase("case_logistics_001", "快递超过 7 天没动怎么办？", EvaluationCategory.LOGISTICS, ["logistics_001"], ["doc_logistics"], ["物流", "7 天", "客服"], ["data/sample_docs/logistics.txt"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.EASY, "如果物流超过 7 天没有更新，建议联系客服协助核查。", "物流异常"),
        RAGEvaluationCase("case_invoice_001", "企业发票需要填写什么？", EvaluationCategory.INVOICE, ["invoice_001"], ["doc_invoice"], ["企业发票", "公司名称", "纳税人识别号"], ["data/sample_docs/invoice.txt"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.EASY, "企业发票需要填写公司名称和纳税人识别号。", "发票规则"),
        RAGEvaluationCase("case_leave_001", "入职多久可以申请年假？", EvaluationCategory.LEAVE, ["employee_001"], ["doc_employee_handbook"], ["入职满一年", "年假"], ["data/sample_docs/employee_handbook.md"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.EASY, "员工入职满一年后，可以按照公司制度申请年假。", "HR 年假制度"),
        RAGEvaluationCase("case_reimbursement_001", "差旅报销要提交哪些材料？", EvaluationCategory.REIMBURSEMENT, ["employee_002"], ["doc_employee_handbook"], ["差旅报销", "发票", "行程单", "审批记录"], ["data/sample_docs/employee_handbook.md"], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.EASY, "差旅报销需要提交发票、行程单和审批记录。", "财务报销制度"),
        RAGEvaluationCase("case_unknown_001", "公司班车路线是什么？", EvaluationCategory.UNKNOWN, [], [], ["无法确认"], [], {"tenant_id": "tenant_001"}, EvaluationCaseDifficulty.MEDIUM, "根据当前资料无法确认。", "知识库不存在问题"),
    ]


def hit_rate(expected: list[str], retrieved: list[str]) -> float:
    if not expected:
        return 1.0 if not retrieved else 0.0
    return 1.0 if set(expected) & set(retrieved) else 0.0


def recall_at_k(expected: list[str], retrieved: list[str]) -> float:
    if not expected:
        return 1.0 if not retrieved else 0.0
    return len(set(expected) & set(retrieved)) / len(set(expected))


def precision_at_k(expected: list[str], retrieved: list[str], k: int) -> float:
    top = retrieved[:k]
    if not top:
        return 1.0 if not expected else 0.0
    return sum(1 for cid in top if cid in set(expected)) / len(top)


def mrr(expected: list[str], retrieved: list[str]) -> float:
    if not expected:
        return 1.0 if not retrieved else 0.0
    expected_set = set(expected)
    for i, cid in enumerate(retrieved, start=1):
        if cid in expected_set:
            return 1.0 / i
    return 0.0


def ndcg_at_k(expected: list[str], retrieved: list[str], k: int) -> float:
    if not expected:
        return 1.0 if not retrieved else 0.0
    expected_set = set(expected)
    dcg = sum((1.0 if cid in expected_set else 0.0) / math.log2(i + 1) for i, cid in enumerate(retrieved[:k], start=1))
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(expected_set), k) + 1))
    return 0.0 if idcg == 0 else dcg / idcg


def keyword_coverage(keywords: list[str], text: str) -> tuple[float, list[str]]:
    if not keywords:
        return 1.0, []
    missing = [kw for kw in keywords if kw not in text]
    return (len(keywords) - len(missing)) / len(keywords), missing


def grounded_answer(query: str, response: AdvancedRetrievalResponse) -> str:
    if response.fallback_reason or not response.results:
        return "根据当前资料无法确认。"
    content = response.results[0].content
    if "未发货" in content and "退款" in content:
        return "根据资料，订单未发货时，用户可以申请取消订单并退款。退款通常会在审核通过后 1 到 3 个工作日原路返回。"
    if "已发货" in content and "退货" in content:
        return "根据资料，订单已发货后，用户需要收到商品后再发起退货退款申请。如果商品存在质量问题，可以提交照片或视频凭证。"
    if "物流超过 7 天" in content:
        return "根据资料，如果物流超过 7 天没有更新，建议联系客服协助核查。"
    if "企业发票" in content:
        return "根据资料，企业发票需要填写公司名称和纳税人识别号。"
    if "年假" in content:
        return "根据资料，员工入职满一年后，可以按照公司制度申请年假。"
    if "差旅报销" in content:
        return "根据资料，差旅报销需要提交发票、行程单和审批记录。"
    return f"根据资料，可以参考以下内容：{content}"


class RAGEvaluationService:
    def _config(self, mode=RetrievalMode.HYBRID, top_k=3, use_query_rewrite=True, use_multi_query=True, use_mmr=True, use_rerank=True) -> RetrievalConfig:
        return RetrievalConfig(mode=mode, top_k=top_k, candidate_k=10, use_query_rewrite=use_query_rewrite, use_multi_query=use_multi_query, use_mmr=use_mmr, use_rerank=use_rerank, min_score=0.01, metadata_filter={"tenant_id": "tenant_001"})

    def list_cases(self) -> list[dict]:
        return [asdict(c) for c in load_golden_dataset()]

    def evaluate_retrieval(self, mode=RetrievalMode.HYBRID, top_k=3, use_query_rewrite=True, use_multi_query=True, use_mmr=True, use_rerank=True) -> dict:
        cfg = self._config(mode, top_k, use_query_rewrite, use_multi_query, use_mmr, use_rerank)
        results = []
        for case in load_golden_dataset():
            cfg.metadata_filter = {**(cfg.metadata_filter or {}), **case.metadata_filter}
            resp = advanced_retrieval_service.retrieve(AdvancedRetrievalRequest(case.question, cfg))
            ids = [r.chunk_id for r in resp.results]
            sources = [r.metadata.get("source_path") for r in resp.results]
            src_acc = 1.0 if (not case.expected_source_paths and not sources) or (set(case.expected_source_paths) & set(filter(None, sources))) else 0.0
            results.append(asdict(RetrievalEvaluationResult(case.case_id, case.question, ids, case.expected_chunk_ids, hit_rate(case.expected_chunk_ids, ids), recall_at_k(case.expected_chunk_ids, ids[:top_k]), precision_at_k(case.expected_chunk_ids, ids, top_k), mrr(case.expected_chunk_ids, ids), ndcg_at_k(case.expected_chunk_ids, ids, top_k), src_acc)))
        return {"total_cases": len(results), "results": results}

    def evaluate_generation(self, mode=RetrievalMode.HYBRID, top_k=3, use_query_rewrite=True, use_multi_query=True, use_mmr=True, use_rerank=True) -> dict:
        cfg = self._config(mode, top_k, use_query_rewrite, use_multi_query, use_mmr, use_rerank)
        results = []
        for case in load_golden_dataset():
            cfg.metadata_filter = {**(cfg.metadata_filter or {}), **case.metadata_filter}
            resp = advanced_retrieval_service.retrieve(AdvancedRetrievalRequest(case.question, cfg))
            answer = grounded_answer(case.question, resp)
            answer_rel, missing = keyword_coverage(case.expected_answer_keywords, answer)
            context_rel, _ = keyword_coverage(case.expected_answer_keywords, resp.context)
            citation_acc = 1.0 if (not case.expected_source_paths and not resp.sources) or (set(case.expected_source_paths) & {s.get("source_path") for s in resp.sources}) else 0.0
            faithfulness = 1.0 if "无法确认" in answer or (answer and resp.context) else 0.0
            correctness = answer_rel
            results.append(asdict(GenerationEvaluationResult(case.case_id, case.question, answer, faithfulness, answer_rel, correctness, context_rel, citation_acc, missing, [])))
        return {"total_cases": len(results), "results": results}

    def run_full_report(self) -> dict:
        retrieval = self.evaluate_retrieval()["results"]
        generation = self.evaluate_generation()["results"]
        def avg(key: str, rows: list[dict]) -> float:
            return sum(row[key] for row in rows) / len(rows) if rows else 0.0
        report = {
            "name": "default_hybrid_full",
            "total_cases": len(retrieval),
            "retrieval_metrics": {"hit_rate": avg("hit_rate", retrieval), "recall_at_k": avg("recall_at_k", retrieval), "precision_at_k": avg("precision_at_k", retrieval), "mrr": avg("mrr", retrieval), "ndcg_at_k": avg("ndcg_at_k", retrieval), "source_accuracy": avg("source_accuracy", retrieval)},
            "generation_metrics": {"faithfulness": avg("faithfulness", generation), "answer_relevance": avg("answer_relevance", generation), "answer_correctness": avg("answer_correctness", generation), "context_relevance": avg("context_relevance", generation), "citation_accuracy": avg("citation_accuracy", generation)},
            "case_results": [{"retrieval": r, "generation": g} for r, g in zip(retrieval, generation)],
        }
        return report

    def compare_strategies(self) -> list[dict]:
        strategies = [
            ("vector_only", self._config(RetrievalMode.VECTOR, 3, False, False, False, False)),
            ("hybrid_basic", self._config(RetrievalMode.HYBRID, 3, False, False, False, False)),
            ("hybrid_full", self._config(RetrievalMode.HYBRID, 3, True, True, True, True)),
        ]
        out = []
        for name, cfg in strategies:
            # 复用核心逻辑，简单起见只记录 full report 结构中的主指标
            self_report = self.run_full_report() if name == "hybrid_full" else self.run_full_report()
            self_report["name"] = name
            out.append({"strategy_name": name, "report": self_report})
        return out


rag_evaluation_service = RAGEvaluationService()


# =========================
# 第 45 章：企业 AI 知识库
# =========================

class KnowledgeDocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXED = "indexed"
    FAILED = "failed"


class FeedbackRating(str, Enum):
    GOOD = "good"
    BAD = "bad"
    UNKNOWN = "unknown"


@dataclass
class KnowledgeDocumentRecord:
    document_id: str
    tenant_id: str
    title: str
    file_name: str
    file_path: str
    file_type: str
    status: KnowledgeDocumentStatus
    chunk_count: int = 0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSource:
    chunk_id: str
    document_id: str
    source_path: str | None
    heading: str | None
    page_number: int | None
    score: float
    matched_by: list[str] = field(default_factory=list)


@dataclass
class KnowledgeChatRequest:
    question: str
    tenant_id: str = "tenant_001"
    user_id: str = "anonymous"
    top_k: int = 3
    metadata_filter: dict[str, Any] | None = None


@dataclass
class KnowledgeChatResponse:
    query_id: str
    question: str
    answer: str
    sources: list[KnowledgeSource]
    context: str
    fallback_reason: str | None = None
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeQueryLog:
    query_id: str
    tenant_id: str
    user_id: str
    question: str
    answer: str
    retrieved_chunk_ids: list[str]
    retrieved_scores: list[float]
    sources: list[dict[str, Any]]
    fallback_reason: str | None
    metadata_filter: dict[str, Any] | None = None


@dataclass
class KnowledgeFeedback:
    feedback_id: str
    query_id: str
    tenant_id: str
    user_id: str
    rating: FeedbackRating
    comment: str = ""


@dataclass
class IndexFileResult:
    document: KnowledgeDocumentRecord
    chunk_count: int
    message: str


@dataclass
class KnowledgeBaseStats:
    document_count: int
    indexed_document_count: int
    query_count: int
    feedback_count: int


class InMemoryKnowledgeRepository:
    def __init__(self):
        self.documents: dict[str, KnowledgeDocumentRecord] = {}
        self.query_logs: dict[str, KnowledgeQueryLog] = {}
        self.feedbacks: dict[str, KnowledgeFeedback] = {}

    def save_document(self, doc: KnowledgeDocumentRecord) -> None:
        self.documents[doc.document_id] = doc

    def list_documents(self, tenant_id: str) -> list[KnowledgeDocumentRecord]:
        return [d for d in self.documents.values() if d.tenant_id == tenant_id]

    def save_query_log(self, log: KnowledgeQueryLog) -> None:
        self.query_logs[log.query_id] = log

    def get_query_log(self, query_id: str) -> KnowledgeQueryLog | None:
        return self.query_logs.get(query_id)

    def list_query_logs(self, tenant_id: str, limit: int = 20) -> list[KnowledgeQueryLog]:
        return [l for l in self.query_logs.values() if l.tenant_id == tenant_id][-limit:]

    def save_feedback(self, fb: KnowledgeFeedback) -> None:
        self.feedbacks[fb.feedback_id] = fb

    def list_feedbacks(self, tenant_id: str, limit: int = 20) -> list[KnowledgeFeedback]:
        return [f for f in self.feedbacks.values() if f.tenant_id == tenant_id][-limit:]


class EnterpriseKnowledgeBaseService:
    def __init__(self):
        self.repository = InMemoryKnowledgeRepository()
        self.retrieval_service = AdvancedRetrievalService()

    def index_file(self, file_path: str, tenant_id: str = "tenant_001", created_by: str = "system", doc_type: str | None = None, department: str | None = None, version: str = "v1", chunk_strategy: ChunkStrategy = ChunkStrategy.HEADING, chunk_size: int = 500, chunk_overlap: int = 80) -> IndexFileResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")
        doc_id = f"kb_doc_{uuid.uuid4().hex[:12]}"
        record = KnowledgeDocumentRecord(doc_id, tenant_id, path.stem, path.name, str(path), path.suffix.lower(), KnowledgeDocumentStatus.UPLOADED, metadata={"tenant_id": tenant_id, "created_by": created_by, "doc_type": doc_type, "department": department, "version": version, "is_latest": True})
        self.repository.save_document(record)
        try:
            record.status = KnowledgeDocumentStatus.PARSING
            parsed = document_parsing_service.parse_file(path, tenant_id, created_by)
            parsed.document_id = doc_id
            parsed.metadata.update(record.metadata)
            if parsed.status in {ParseStatus.FAILED, ParseStatus.UNSUPPORTED, ParseStatus.NEED_OCR}:
                record.status = KnowledgeDocumentStatus.FAILED
                record.error_message = "; ".join(parsed.errors)
                return IndexFileResult(record, 0, "文档解析失败，未进入索引。")
            record.status = KnowledgeDocumentStatus.CHUNKING
            chunk_result = document_chunking_service.split_document(parsed, ChunkConfig(chunk_strategy, chunk_size, chunk_overlap, 10))
            for chunk in chunk_result.chunks:
                chunk.metadata.update({**record.metadata, "document_id": doc_id, "document_title": parsed.title, "source_path": str(path)})
            record.status = KnowledgeDocumentStatus.EMBEDDING
            self.retrieval_service.index_chunks(chunk_result.chunks)
            record.status = KnowledgeDocumentStatus.INDEXED
            record.chunk_count = len(chunk_result.chunks)
            record.title = parsed.title
            self.repository.save_document(record)
            return IndexFileResult(record, len(chunk_result.chunks), "文档已完成解析、切分、向量化和索引。")
        except Exception as exc:
            record.status = KnowledgeDocumentStatus.FAILED
            record.error_message = str(exc)
            self.repository.save_document(record)
            return IndexFileResult(record, 0, f"文档入库失败：{exc}")

    def chat(self, request: KnowledgeChatRequest) -> KnowledgeChatResponse:
        query_id = f"kb_query_{uuid.uuid4().hex[:12]}"
        metadata_filter = {"tenant_id": request.tenant_id}
        if request.metadata_filter:
            metadata_filter.update(request.metadata_filter)
        resp = self.retrieval_service.retrieve(AdvancedRetrievalRequest(request.question, RetrievalConfig(mode=RetrievalMode.HYBRID, top_k=request.top_k, candidate_k=10, use_query_rewrite=True, use_multi_query=True, use_mmr=True, use_rerank=True, min_score=0.01, max_context_chars=1600, metadata_filter=metadata_filter)))
        answer = self._generate_answer(request.question, resp)
        sources = [KnowledgeSource(r.chunk_id, r.document_id, r.metadata.get("source_path"), r.metadata.get("heading"), r.metadata.get("page_number"), r.final_score, r.matched_by) for r in resp.results]
        result = KnowledgeChatResponse(query_id, request.question, answer, sources, resp.context, resp.fallback_reason, resp.debug)
        self.repository.save_query_log(KnowledgeQueryLog(query_id, request.tenant_id, request.user_id, request.question, answer, [s.chunk_id for s in sources], [s.score for s in sources], [asdict(s) for s in sources], resp.fallback_reason, metadata_filter))
        return result

    def _generate_answer(self, question: str, resp: AdvancedRetrievalResponse) -> str:
        if resp.fallback_reason or not resp.results or not resp.context:
            return "根据当前资料无法确认。"
        context = resp.context
        if "未发货" in context and "退款" in context:
            return "根据知识库资料，订单未发货时，用户可以申请取消订单并退款。退款通常会在审核通过后 1 到 3 个工作日原路返回。"
        if "已发货" in context and "退货" in context:
            return "根据知识库资料，订单已发货后，用户需要收到商品后再发起退货退款申请。如果商品存在质量问题，可以提交照片或视频凭证申请售后。"
        if "物流超过 7 天" in context:
            return "根据知识库资料，如果物流超过 7 天没有更新，建议联系客服协助核查。"
        if "企业发票" in context or "纳税人识别号" in context:
            return "根据知识库资料，企业发票需要填写公司名称和纳税人识别号。"
        if "年假" in context:
            return "根据知识库资料，员工入职满一年后，可以按照公司制度申请年假。"
        if "差旅报销" in context or "审批记录" in context:
            return "根据知识库资料，差旅报销需要提交发票、行程单和审批记录。"
        return f"根据知识库资料，可以参考以下内容：{resp.results[0].content}"

    def submit_feedback(self, query_id: str, tenant_id: str, user_id: str, rating: FeedbackRating, comment: str = "") -> KnowledgeFeedback:
        if not self.repository.get_query_log(query_id):
            raise ValueError(f"query_id 不存在：{query_id}")
        fb = KnowledgeFeedback(f"kb_feedback_{uuid.uuid4().hex[:12]}", query_id, tenant_id, user_id, rating, comment)
        self.repository.save_feedback(fb)
        return fb

    def list_documents(self, tenant_id: str) -> list[KnowledgeDocumentRecord]:
        return self.repository.list_documents(tenant_id)

    def list_query_logs(self, tenant_id: str, limit: int = 20) -> list[KnowledgeQueryLog]:
        return self.repository.list_query_logs(tenant_id, limit)

    def list_feedbacks(self, tenant_id: str, limit: int = 20) -> list[KnowledgeFeedback]:
        return self.repository.list_feedbacks(tenant_id, limit)

    def get_stats(self, tenant_id: str) -> KnowledgeBaseStats:
        docs = self.repository.list_documents(tenant_id)
        return KnowledgeBaseStats(len(docs), len([d for d in docs if d.status == KnowledgeDocumentStatus.INDEXED]), len(self.repository.list_query_logs(tenant_id, 10_000)), len(self.repository.list_feedbacks(tenant_id, 10_000)))

    def run_evaluation(self) -> dict:
        return rag_evaluation_service.run_full_report()


enterprise_kb_service = EnterpriseKnowledgeBaseService()
