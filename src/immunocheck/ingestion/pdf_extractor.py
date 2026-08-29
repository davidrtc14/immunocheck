from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


class PdfExtractionError(RuntimeError):
    """Indica que um PDF não pôde ser extraído de maneira confiável."""


def extract_pdf(path: Path, metadata: DocumentMetadata) -> ExtractedDocument:
    if metadata.format != "pdf":
        raise PdfExtractionError("O metadado do documento não indica formato PDF.")
    if path.suffix.lower() != ".pdf":
        raise PdfExtractionError("O arquivo informado não possui extensão PDF.")

    try:
        reader = PdfReader(path)
    except Exception as exc:
        raise PdfExtractionError(f"Não foi possível abrir o PDF: {path.name}") from exc

    pages: list[ExtractedPage] = []
    empty_pages: list[int] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = _normalize_extracted_text(page.extract_text() or "")
        except Exception as exc:
            raise PdfExtractionError(f"Falha ao extrair a página {page_number}.") from exc
        if not text:
            empty_pages.append(page_number)
        pages.append(ExtractedPage(number=page_number, text=text))

    if not pages:
        raise PdfExtractionError("O PDF não contém páginas.")
    if all(not page.text for page in pages):
        raise PdfExtractionError("O PDF não contém texto selecionável; OCR é necessário.")

    warnings = ()
    if empty_pages:
        preview = ", ".join(str(number) for number in empty_pages[:10])
        warnings = (f"Páginas sem texto extraído: {preview}",)
    return ExtractedDocument(metadata=metadata, pages=tuple(pages), extraction_warnings=warnings)


def _normalize_extracted_text(text: str) -> str:
    lines = (" ".join(line.split()) for line in text.replace("\x00", "").splitlines())
    return "\n".join(line for line in lines if line)
