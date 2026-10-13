from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterator

from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


class XmlExtractionError(RuntimeError):
    """Indica que um documento XML não produziu conteúdo textual útil."""


HEADING_TAGS = {"article-title", "title"}
BLOCK_TAGS = {
    "article-title",
    "kwd",
    "license-p",
    "p",
    "td",
    "th",
    "title",
}


def extract_xml(xml: str, metadata: DocumentMetadata) -> ExtractedDocument:
    if metadata.format != "xml":
        raise XmlExtractionError("O metadado do documento não indica formato XML.")
    if not xml.strip():
        raise XmlExtractionError("O XML recebido está vazio.")
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise XmlExtractionError(f"O XML recebido é inválido: {exc}") from exc

    article = root if _local_name(root.tag) == "article" else root.find(".//article")
    if article is None:
        raise XmlExtractionError("O XML não contém um artigo reconhecível.")

    lines: dict[str, bool] = {}
    for element, inside_block in _walk(article, in_block=False):
        if _local_name(element.tag) not in BLOCK_TAGS or inside_block:
            continue
        text = " ".join("".join(element.itertext()).split())
        if text:
            lines.setdefault(text, _local_name(element.tag) in HEADING_TAGS)
    normalized = "\n".join(lines)
    headings: list[tuple[int, str]] = []
    offset = 0
    for line, is_heading in lines.items():
        if is_heading:
            headings.append((offset, line))
        offset += len(line) + 1
    if len(normalized) < 40:
        raise XmlExtractionError("O XML não contém texto útil suficiente.")
    return ExtractedDocument(
        metadata=metadata,
        pages=(ExtractedPage(number=1, text=normalized, headings=tuple(headings)),),
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _walk(
    element: ET.Element,
    *,
    in_block: bool,
) -> Iterator[tuple[ET.Element, bool]]:
    """Percorre o artigo em ordem de documento, em tempo linear, sinalizando blocos aninhados."""
    yield element, in_block
    child_in_block = in_block or _local_name(element.tag) in BLOCK_TAGS
    for child in element:
        yield from _walk(child, in_block=child_in_block)
