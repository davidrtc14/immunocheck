from __future__ import annotations

import hashlib
from pathlib import Path

from immunocheck.ingestion.catalog import CatalogEntry, load_catalog
from immunocheck.ingestion.corpus_versioning import (
    CorpusVersioningError,
    build_corpus_snapshot,
    load_download_receipts,
    publish_corpus_snapshot,
)
from immunocheck.ingestion.html_extractor import HtmlExtractionError, extract_html
from immunocheck.ingestion.models import ExtractedDocument
from immunocheck.ingestion.pdf_extractor import PdfExtractionError, extract_pdf

PROJECT_ROOT = Path(__file__).parents[1]
CATALOG_PATH = PROJECT_ROOT / "corpus" / "catalog.csv"
RAW_DIR = PROJECT_ROOT / "corpus" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "corpus" / "processed"


def main() -> None:
    try:
        snapshot = build_corpus_snapshot(
            load_catalog(CATALOG_PATH),
            load_download_receipts(RAW_DIR / "downloads.json"),
            RAW_DIR,
            _extract,
            previous_manifest_path=PROCESSED_DIR / "manifest.json",
            previous_chunks_path=PROCESSED_DIR / "chunks.jsonl",
        )
        publish_corpus_snapshot(
            snapshot,
            chunks_path=PROCESSED_DIR / "chunks.jsonl",
            report_path=PROCESSED_DIR / "validation_report.json",
            manifest_path=PROCESSED_DIR / "manifest.json",
        )
    except (CorpusVersioningError, HtmlExtractionError, PdfExtractionError) as exc:
        print(f"FALHA: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc

    for item in snapshot.report:
        print(
            f"{item['document_id']}: {item['action']} | {item['pages']} página(s) | "
            f"{item['chunks']} trecho(s)"
        )
    print(
        f"Corpus {snapshot.manifest['corpus_version']}: "
        f"{snapshot.manifest['document_count']} documento(s), "
        f"{snapshot.manifest['chunk_count']} trecho(s)."
    )
    print(
        "Mudanças: "
        f"{len(snapshot.changes.added)} novo(s), "
        f"{len(snapshot.changes.reprocessed)} reprocessado(s), "
        f"{len(snapshot.changes.metadata_updated)} metadado(s) atualizado(s), "
        f"{len(snapshot.changes.reused)} reutilizado(s), "
        f"{len(snapshot.changes.removed)} removido(s)."
    )


def _extract(path: Path, entry: CatalogEntry) -> ExtractedDocument:
    if entry.metadata.format == "pdf":
        return extract_pdf(path, entry.metadata)
    html = path.read_text(encoding="utf-8-sig", errors="replace")
    return extract_html(html, entry.metadata)


def _verify_download(path: Path, receipt: dict[str, object]) -> None:
    """Compatibilidade com os testes do primeiro corte vertical."""
    content = path.read_bytes()
    expected_size = receipt["size_bytes"]
    expected_hash = receipt["sha256"]
    if len(content) != expected_size:
        raise ValueError(f"Tamanho divergente do recibo para {path.name}.")
    if hashlib.sha256(content).hexdigest() != expected_hash:
        raise ValueError(f"SHA-256 divergente do recibo para {path.name}.")


if __name__ == "__main__":
    main()
