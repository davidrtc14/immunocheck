"""Diagnostica a fase A usando somente a calibração v2 já executada."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_diagnostics import (
    analyze_refinement_phase_a,
    render_refinement_diagnostics,
)
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
DEFAULT_RECORDS = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "evaluation/results/refinement_v2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    json_output = args.output_dir / "calibration_phase_a_diagnostics.json"
    markdown_output = args.output_dir / "CALIBRATION_PHASE_A_DIAGNOSTICS.md"
    if not args.overwrite and (json_output.exists() or markdown_output.exists()):
        parser.error("O diagnóstico já existe; use --overwrite apenas para reprodução.")

    items = load_end_to_end_items(args.dataset, require_reviewed=True)
    records = load_refinement_checkpoint(args.records)
    report = analyze_refinement_phase_a(records, items)
    report["inputs"] = {
        "dataset": str(args.dataset.relative_to(ROOT)).replace("\\", "/"),
        "dataset_sha256": _sha256(args.dataset),
        "records": str(args.records.relative_to(ROOT)).replace("\\", "/"),
        "records_sha256": _sha256(args.records),
        "v1_test_records_loaded": 0,
        "holdout_v2_records_loaded": 0,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_output.write_text(
        render_refinement_diagnostics(report), encoding="utf-8", newline="\n"
    )
    print(json_output.relative_to(ROOT))
    print(markdown_output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
