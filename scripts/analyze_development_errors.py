"""Audita a origem observável dos erros da iteração v2 sem carregar o teste."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from immunocheck.evaluation.development_end_to_end import load_checkpoint, sha256_file
from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items
from immunocheck.evaluation.error_attribution import (
    analyze_development_error_attribution,
    render_error_attribution_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "evaluation" / "end_to_end" / "items.jsonl"
DEFAULT_RECORDS = (
    ROOT / "evaluation" / "results" / "development" / "end_to_end_v2_records.jsonl"
)
DEFAULT_OUTPUT_DIR = ROOT / "evaluation" / "results" / "refinement_v2"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    json_output = args.output_dir / "development_error_attribution.json"
    markdown_output = args.output_dir / "DEVELOPMENT_ERROR_ATTRIBUTION.md"
    existing = [path for path in (json_output, markdown_output) if path.exists()]
    if existing and not args.overwrite:
        parser.error("A auditoria já existe; use --overwrite somente para reprodução declarada.")

    all_items = load_end_to_end_items(args.dataset, require_reviewed=True)
    development = tuple(item for item in all_items if item.split is DatasetSplit.DEVELOPMENT)
    records = load_checkpoint(args.records)
    report = analyze_development_error_attribution(records, development)
    report["inputs"] = {
        "dataset": str(args.dataset.relative_to(ROOT)),
        "dataset_sha256": sha256_file(args.dataset),
        "records": str(args.records.relative_to(ROOT)),
        "records_sha256": sha256_file(args.records),
        "test_records_loaded": 0,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_output.write_text(render_error_attribution_markdown(report), encoding="utf-8")
    print(json_output.relative_to(ROOT))
    print(markdown_output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
