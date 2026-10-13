from __future__ import annotations

from bs4 import BeautifulSoup

from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


class HtmlExtractionError(RuntimeError):
    """Indica que uma página HTML não produziu conteúdo textual útil."""


HEADING_TAGS = ("h1", "h2", "h3", "h4")
REMOVABLE_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "form", "aside")


def extract_html(html: str, metadata: DocumentMetadata) -> ExtractedDocument:
    if metadata.format != "html":
        raise HtmlExtractionError("O metadado do documento não indica formato HTML.")
    if not html.strip():
        raise HtmlExtractionError("O HTML recebido está vazio.")

    soup = BeautifulSoup(html, "html.parser")
    for element in soup(REMOVABLE_TAGS):
        element.decompose()

    content = soup.find("main") or soup.find("article") or soup.body
    if content is None:
        raise HtmlExtractionError("A página não contém uma área textual reconhecível.")

    pending_headings = [
        " ".join(tag.get_text(" ").split()) for tag in content.find_all(HEADING_TAGS)
    ]
    pending_headings = [heading for heading in pending_headings if heading]
    lines = (" ".join(line.split()) for line in content.get_text("\n").splitlines())
    kept: list[str] = []
    headings: list[tuple[int, str]] = []
    offset = 0
    for line in lines:
        if not line:
            continue
        if pending_headings and line == pending_headings[0]:
            headings.append((offset, line))
            pending_headings.pop(0)
        kept.append(line)
        offset += len(line) + 1
    text = "\n".join(kept)
    if len(text) < 40:
        raise HtmlExtractionError("A página não contém texto útil suficiente.")

    return ExtractedDocument(
        metadata=metadata,
        pages=(ExtractedPage(number=1, text=text, headings=tuple(headings)),),
    )
