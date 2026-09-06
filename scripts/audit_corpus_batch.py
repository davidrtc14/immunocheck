from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from immunocheck.ingestion.batch_audit import audit_download
from immunocheck.ingestion.catalog import load_catalog
from immunocheck.ingestion.corpus_versioning import load_download_receipts

PROJECT_ROOT = Path(__file__).parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita um lote sem publicar ou aprovar fontes.")
    parser.add_argument("--batch", required=True, help="Número do lote, por exemplo 002.")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]{3}", args.batch):
        parser.error("O lote deve ter exatamente três dígitos.")
    reviews_dir = PROJECT_ROOT / "corpus" / "reviews"
    with (reviews_dir / f"batch_{args.batch}.csv").open(encoding="utf-8", newline="") as file:
        document_ids = [row["document_id"] for row in csv.DictReader(file)]
    if not document_ids or len(document_ids) != len(set(document_ids)):
        parser.error("O lote está vazio ou contém IDs repetidos.")
    entries = {
        entry.metadata.document_id: entry
        for entry in load_catalog(PROJECT_ROOT / "corpus" / "catalog.csv")
    }
    raw_dir = PROJECT_ROOT / "corpus" / "raw"
    receipts = {
        receipt.document_id: receipt
        for receipt in load_download_receipts(raw_dir / "downloads.json")
    }
    if set(document_ids).difference(entries):
        parser.error("O lote contém IDs ausentes do catálogo.")
    text_dir = raw_dir / "reviews" / f"batch_{args.batch}"
    text_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    failures = []
    for document_id in document_ids:
        try:
            if document_id not in receipts:
                raise ValueError("Sem recibo de download; consultar o histórico de coleta.")
            report, document = audit_download(entries[document_id], receipts[document_id], raw_dir)
        except (OSError, ValueError, RuntimeError, KeyError) as exc:
            failures.append({"document_id": document_id, "error": str(exc)})
            continue
        # Textos completos são locais e ignorados pelo Git, nunca vão para o relatório público.
        review_text = "\n\n".join(
            f"--- Página física {page.number} ---\n{page.text}" for page in document.pages
        )
        (text_dir / f"{document_id}.txt").write_text(review_text + "\n", encoding="utf-8")
        reports.append(report)
        print(
            f"{document_id}: {report['pages']} página(s), {report['characters']} caracteres, "
            f"{report['chunks']} chunks potenciais"
        )
    hashes: dict[str, list[str]] = {}
    for report in reports:
        hashes.setdefault(str(report["text_sha256"]), []).append(str(report["document_id"]))
    payload = {
        "batch": args.batch,
        "scope": "technical_only_not_human_approval",
        "documents": reports,
        "failures": failures,
        "exact_text_duplicates_within_batch": [ids for ids in hashes.values() if len(ids) > 1],
        "raw_duplicates_against_validated_catalog": [
            {"document_id": report["document_id"], "validated_document_id": document_id}
            for report in reports
            for document_id, receipt in receipts.items()
            if document_id != report["document_id"]
            and document_id in entries
            and entries[document_id].status == "validated"
            and receipt.sha256 == report["raw_sha256"]
        ],
    }
    # Apenas metadados e métricas, sem corpo textual dos documentos.
    (reviews_dir / f"batch_{args.batch}.audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failures:
        print(f"Falha técnica em {len(failures)} documento(s); consultar o relatório.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
