from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from immunocheck.ingestion.catalog import CatalogEntry, load_catalog
from immunocheck.ingestion.chunker import chunk_document
from immunocheck.ingestion.html_extractor import HtmlExtractionError, extract_html
from immunocheck.ingestion.models import ExtractedDocument
from immunocheck.ingestion.pdf_extractor import PdfExtractionError, extract_pdf

PROJECT_ROOT = Path(__file__).parents[1]
CATALOG_PATH = PROJECT_ROOT / "corpus" / "catalog.csv"
RAW_DIR = PROJECT_ROOT / "corpus" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "corpus" / "processed"


def main() -> None:
    entries = {entry.metadata.document_id: entry for entry in load_catalog(CATALOG_PATH)}
    receipts = json.loads((RAW_DIR / "downloads.json").read_text(encoding="utf-8"))
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    report: list[dict[str, object]] = []
    chunks = []
    for receipt in receipts:
        document_id = receipt["document_id"]
        entry = entries[document_id]
        path = RAW_DIR / receipt["relative_path"]
        print(f"Processando {document_id}...")
        try:
            _verify_download(path, receipt)
            document = _extract(path, entry)
            document_chunks = chunk_document(document)
            if not document_chunks:
                raise ValueError("A segmentação não produziu trechos.")
        except (HtmlExtractionError, PdfExtractionError, OSError, ValueError) as exc:
            report.append(
                {
                    "document_id": document_id,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"  FALHA: {type(exc).__name__}: {exc}")
            continue

        chunks.extend(document_chunks)
        character_count = sum(len(page.text) for page in document.pages)
        report.append(
            {
                "document_id": document_id,
                "status": "validated",
                "pages": len(document.pages),
                "characters": character_count,
                "chunks": len(document_chunks),
                "warnings": list(document.extraction_warnings),
            }
        )
        print(
            f"  {len(document.pages)} página(s) | {character_count} caracteres | "
            f"{len(document_chunks)} trecho(s)"
        )

    with (PROCESSED_DIR / "chunks.jsonl").open("w", encoding="utf-8") as output:
        for chunk in chunks:
            output.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
    (PROCESSED_DIR / "validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    failures = [item for item in report if item["status"] == "failed"]
    print(
        f"Corpus processado: {len(report) - len(failures)} documento(s), {len(chunks)} trecho(s)."
    )
    if failures:
        raise SystemExit(1)


def _extract(path: Path, entry: CatalogEntry) -> ExtractedDocument:
    if entry.metadata.format == "pdf":
        return extract_pdf(path, entry.metadata)
    html = path.read_text(encoding="utf-8-sig", errors="replace")
    return extract_html(html, entry.metadata)


def _verify_download(path: Path, receipt: dict[str, object]) -> None:
    content = path.read_bytes()
    expected_size = receipt["size_bytes"]
    expected_hash = receipt["sha256"]
    if len(content) != expected_size:
        raise ValueError(f"Tamanho divergente do recibo para {path.name}.")
    if hashlib.sha256(content).hexdigest() != expected_hash:
        raise ValueError(f"SHA-256 divergente do recibo para {path.name}.")


if __name__ == "__main__":
    main()
