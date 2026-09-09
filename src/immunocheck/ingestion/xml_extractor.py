from __future__ import annotations

import xml.etree.ElementTree as ET

from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


class XmlExtractionError(RuntimeError):
    """Indica que um documento XML não produziu conteúdo textual útil."""


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

    lines: list[str] = []
    for element in article.iter():
        if _local_name(element.tag) not in BLOCK_TAGS:
            continue
        if any(_local_name(parent.tag) in BLOCK_TAGS for parent in _ancestors(article, element)):
            continue
        text = " ".join("".join(element.itertext()).split())
        if text:
            lines.append(text)
    normalized = "\n".join(dict.fromkeys(lines))
    if len(normalized) < 40:
        raise XmlExtractionError("O XML não contém texto útil suficiente.")
    return ExtractedDocument(
        metadata=metadata,
        pages=(ExtractedPage(number=1, text=normalized),),
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _ancestors(root: ET.Element, target: ET.Element) -> tuple[ET.Element, ...]:
    path: list[ET.Element] = []

    def visit(element: ET.Element) -> bool:
        if element is target:
            return True
        for child in element:
            path.append(element)
            if visit(child):
                return True
            path.pop()
        return False

    visit(root)
    return tuple(path)
