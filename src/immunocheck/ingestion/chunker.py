from __future__ import annotations

import hashlib
import re

from immunocheck.ingestion.models import ExtractedDocument, ExtractedPage, TextChunk

PARAGRAPH_BREAK = re.compile(r"\n{2,}")
ANCHORED_FORMATS = frozenset({"html", "xml"})
MAX_HEADING_CHARS = 120


def chunk_document(
    document: ExtractedDocument,
    *,
    max_chars: int = 1_200,
    overlap_chars: int = 200,
) -> tuple[TextChunk, ...]:
    if max_chars <= 0:
        raise ValueError("max_chars deve ser positivo.")
    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError("overlap_chars deve ser não negativo e menor que max_chars.")

    chunks: list[TextChunk] = []
    for page in document.pages:
        if not page.text.strip():
            continue
        normalized = _normalize(page.text)
        # Deslocamentos só valem quando a normalização preservou o texto da página.
        anchored = document.metadata.format in ANCHORED_FORMATS and normalized == page.text
        for sequence, (start, text) in enumerate(
            _split_text(normalized, max_chars=max_chars, overlap_chars=overlap_chars),
            start=1,
        ):
            chunk_id = _chunk_id(document.metadata.document_id, page.number, sequence, text)
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    document_id=document.metadata.document_id,
                    text=text,
                    source=document.metadata.source,
                    document_title=document.metadata.title,
                    url=document.metadata.url,
                    page_start=page.number,
                    page_end=page.number,
                    publication_date=document.metadata.publication_date,
                    section=_section_label(page, start) if anchored else None,
                )
            )
    return tuple(chunks)


def _normalize(text: str) -> str:
    return "\n\n".join(part.strip() for part in PARAGRAPH_BREAK.split(text) if part.strip())


def _section_label(page: ExtractedPage, start: int) -> str:
    """Rótulo `Título, §N` da linha onde o chunk começa; HTML/XML não têm páginas reais."""
    paragraph = page.text.count("\n", 0, start) + 1
    heading = next((title for offset, title in reversed(page.headings) if offset <= start), None)
    if heading is None:
        return f"§{paragraph}"
    if len(heading) > MAX_HEADING_CHARS:
        heading = heading[: MAX_HEADING_CHARS - 1].rstrip() + "…"
    return f"{heading}, §{paragraph}"


def _split_text(
    normalized: str,
    *,
    max_chars: int,
    overlap_chars: int,
) -> tuple[tuple[int, str], ...]:
    """Divide o texto e devolve (deslocamento do primeiro caractere útil, chunk)."""
    if not normalized:
        return ()

    chunks: list[tuple[int, str]] = []
    start = 0
    while start < len(normalized):
        end = min(start + max_chars, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary
        raw = normalized[start:end]
        chunk = raw.strip()
        if chunk:
            chunks.append((start + len(raw) - len(raw.lstrip()), chunk))
        if end >= len(normalized):
            break
        start = max(end - overlap_chars, start + 1)
    return tuple(chunks)


def _chunk_id(document_id: str, page: int, sequence: int, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{document_id}:p{page}:c{sequence}:{digest}"
