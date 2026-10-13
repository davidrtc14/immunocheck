from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    document_id: str
    title: str
    source: str
    document_type: str
    publication_date: str | None
    url: str
    format: str


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    number: int
    text: str
    # (deslocamento em `text`, título) das linhas de cabeçalho; só HTML/XML usam âncoras.
    headings: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    metadata: DocumentMetadata
    pages: tuple[ExtractedPage, ...]
    extraction_warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_id: str
    document_id: str
    text: str
    source: str
    document_title: str
    url: str
    page_start: int
    page_end: int
    publication_date: str | None = None
    section: str | None = None
