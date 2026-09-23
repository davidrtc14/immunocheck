from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_annotation_return import (
    inspect_refinement_annotation_return,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evaluation" / "refinement_v2" / "calibration"
DATASET = BASE / "reviewed_items.jsonl"
SELECTION = BASE / "independent_review" / "selection_manifest.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspeciona uma devolução da segunda anotação sem incorporá-la."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(SELECTION.read_text(encoding="utf-8"))
    items = {
        item.item_id: item for item in load_end_to_end_items(DATASET, require_reviewed=True)
    }
    expected = {entry["task_id"]: items[entry["item_id"]] for entry in manifest["mapping"]}
    raw = args.path.read_text(encoding="utf-8-sig")
    inspection = inspect_refinement_annotation_return(raw, expected_tasks=expected)
    report = {
        "schema_version": 1,
        "purpose": "refinement_v2_second_annotation_return_inspection",
        "source_normalized_sha256": hashlib.sha256(
            raw.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        ).hexdigest(),
        "eligible_for_human_gate": inspection.eligible_for_human_gate,
        "reviewer_as_declared": inspection.reviewer,
        "reviewed_at_as_declared": inspection.reviewed_at,
        "parsed_response_count": len(inspection.responses),
        "rejection_reasons": list(inspection.rejection_reasons),
        "agreement": inspection.agreement,
        "raw_return_versioned": False,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if inspection.eligible_for_human_gate else 2


if __name__ == "__main__":
    raise SystemExit(main())
