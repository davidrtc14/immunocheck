from __future__ import annotations

import hashlib
from pathlib import Path

from bs4 import BeautifulSoup

from immunocheck.ingestion.catalog import CatalogEntry
from immunocheck.ingestion.chunker import chunk_document
from immunocheck.ingestion.downloader import SAFE_DOCUMENT_ID, DownloadReceipt
from immunocheck.ingestion.html_extractor import extract_html
from immunocheck.ingestion.models import ExtractedDocument
from immunocheck.ingestion.pdf_extractor import extract_pdf


def audit_download(
    entry: CatalogEntry, receipt: DownloadReceipt, raw_dir: Path
) -> tuple[dict[str, object], ExtractedDocument]:
    """Confere bytes e extração; não concede licença nem aprovação humana."""
    document_id = entry.metadata.document_id
    if not SAFE_DOCUMENT_ID.fullmatch(document_id):
        raise ValueError("document_id inseguro.")
    if receipt.document_id != document_id or receipt.source_url != entry.metadata.url:
        raise ValueError("O recibo não corresponde à entrada do catálogo.")
    path = (raw_dir / receipt.relative_path).resolve()
    if path.parent != raw_dir.resolve():
        raise ValueError("O recibo aponta para fora do diretório de documentos.")
    content = path.read_bytes()
    if len(content) != receipt.size_bytes:
        raise ValueError("Tamanho divergente do recibo.")
    if hashlib.sha256(content).hexdigest() != receipt.sha256:
        raise ValueError("SHA-256 divergente do recibo.")

    if entry.metadata.format == "pdf":
        document = extract_pdf(path, entry.metadata)
        license_text = "\n".join(page.text for page in document.pages)
        license_links: list[str] = []
    else:
        html = content.decode("utf-8-sig", errors="replace")
        document = extract_html(html, entry.metadata)
        soup = BeautifulSoup(html, "html.parser")
        # Examinar o HTML completo, inclusive avisos fora da área textual extraída.
        license_text = soup.get_text(" ", strip=True)
        license_links = sorted(
            {
                str(link["href"])
                for link in soup.find_all("a", href=True)
                if "creativecommons.org/licenses/" in str(link["href"])
            }
        )

    text = "\n\n".join(page.text for page in document.pages)
    normalized_text = " ".join(text.split())
    chunks = chunk_document(document)
    hints = [
        marker
        for marker in (
            "todos os direitos reservados",
            "all rights reserved",
            "creative commons",
            "reprodução parcial ou total",
            "não comercial",
            "não-comercial",
        )
        if marker in " ".join(license_text.lower().split())
    ]
    report: dict[str, object] = {
        "document_id": document_id,
        "title": entry.metadata.title,
        "source_url": receipt.source_url,
        "final_url": receipt.final_url,
        "downloaded_at": receipt.downloaded_at,
        "raw_sha256": receipt.sha256,
        "size_bytes": receipt.size_bytes,
        "text_sha256": hashlib.sha256(normalized_text.encode("utf-8")).hexdigest(),
        "pages": len(document.pages),
        "characters": sum(len(page.text) for page in document.pages),
        "chunks": len(chunks),
        "empty_pages": [page.number for page in document.pages if not page.text],
        "warnings": list(document.extraction_warnings),
        "replacement_characters": text.count("\ufffd"),
        "control_characters": sum(ord(char) < 32 and char not in "\n\r\t" for char in text),
        "license_signals_not_permission": hints,
        "license_links": license_links,
        "human_review": "pending",
    }
    return report, document
