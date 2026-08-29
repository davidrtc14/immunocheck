import json
from pathlib import Path

from immunocheck.ingestion.catalog import load_catalog
from immunocheck.ingestion.downloader import DownloadError, download_catalog_entry, write_receipts

PROJECT_ROOT = Path(__file__).parents[1]
CATALOG_PATH = PROJECT_ROOT / "corpus" / "catalog.csv"
RAW_DIR = PROJECT_ROOT / "corpus" / "raw"


def main() -> None:
    entries = load_catalog(CATALOG_PATH)
    receipts = []
    failures: list[dict[str, str]] = []
    for entry in entries:
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
        receipts.append(receipt)
        print(f"  {receipt.size_bytes} bytes | sha256={receipt.sha256[:12]}...")
    write_receipts(tuple(receipts), RAW_DIR / "downloads.json")
    (RAW_DIR / "download_failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Corpus piloto: {len(receipts)} sucesso(s), {len(failures)} falha(s).")
    print(f"Arquivos locais em {RAW_DIR}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
