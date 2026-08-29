from __future__ import annotations

from bs4 import BeautifulSoup

from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


class HtmlExtractionError(RuntimeError):
    """Indica que uma página HTML não produziu conteúdo textual útil."""


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

    lines = (" ".join(line.split()) for line in content.get_text("\n").splitlines())
    text = "\n".join(line for line in lines if line)
    if len(text) < 40:
        raise HtmlExtractionError("A página não contém texto útil suficiente.")

    return ExtractedDocument(
        metadata=metadata,
        pages=(ExtractedPage(number=1, text=text),),
    )
