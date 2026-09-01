from __future__ import annotations

import argparse
import json
from pathlib import Path

from immunocheck.ingestion.catalog import CatalogEntry, load_catalog
from immunocheck.ingestion.corpus_versioning import load_download_receipts
from immunocheck.ingestion.downloader import (
    DownloadError,
    download_catalog_entry,
    merge_receipts,
    write_receipts,
)

PROJECT_ROOT = Path(__file__).parents[1]
CATALOG_PATH = PROJECT_ROOT / "corpus" / "catalog.csv"
RAW_DIR = PROJECT_ROOT / "corpus" / "raw"


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa um lote incremental do corpus auditável.")
    parser.add_argument(
        "--document-id",
        action="append",
        default=[],
        help="ID a baixar; pode ser repetido. Sem IDs, seleciona pelo estado.",
    )
    parser.add_argument(
        "--status",
        action="append",
        choices=("candidate", "downloaded", "validated", "rejected"),
        default=[],
        help="Estado a selecionar quando nenhum --document-id for informado (padrão: candidate).",
    )
    args = parser.parse_args()

    entries = load_catalog(CATALOG_PATH)
    selected = _select_entries(entries, tuple(args.document_id), tuple(args.status))
    existing = (
        load_download_receipts(RAW_DIR / "downloads.json")
        if (RAW_DIR / "downloads.json").exists()
        else ()
    )
    downloaded = []
    failures: list[dict[str, str]] = []
    for entry in selected:
        print(f"Baixando {entry.metadata.document_id}...")
        try:
            receipt = download_catalog_entry(entry, RAW_DIR)
        except DownloadError as exc:
            failures.append(
                {
                    "document_id": entry.metadata.document_id,
                    "url": entry.metadata.url,
                    "error": str(exc),
                }
            )
            print(f"  FALHA: {exc}")
            continue
        downloaded.append(receipt)
        print(f"  {receipt.size_bytes} bytes | sha256={receipt.sha256[:12]}...")

    write_receipts(merge_receipts(existing, tuple(downloaded)), RAW_DIR / "downloads.json")
    (RAW_DIR / "download_failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Lote: {len(downloaded)} sucesso(s), {len(failures)} falha(s).")
    if failures:
        raise SystemExit(1)


def _select_entries(
    entries: tuple[CatalogEntry, ...],
    document_ids: tuple[str, ...],
    statuses: tuple[str, ...],
) -> tuple[CatalogEntry, ...]:
    if document_ids:
        requested = set(document_ids)
        available = {entry.metadata.document_id for entry in entries}
        unknown = sorted(requested.difference(available))
        if unknown:
            raise SystemExit("IDs ausentes do catálogo: " + ", ".join(unknown))
        return tuple(entry for entry in entries if entry.metadata.document_id in requested)
    selected_statuses = set(statuses or ("candidate",))
    return tuple(entry for entry in entries if entry.status in selected_statuses)


if __name__ == "__main__":
    main()
