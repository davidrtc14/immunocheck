from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.annotation_agreement import (
    compute_annotation_agreement,
    load_annotation_responses,
)
from immunocheck.evaluation.end_to_end import EndToEndDatasetError, load_end_to_end_items

ROOT = Path(__file__).parents[1] / "evaluation" / "end_to_end"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Concordância pré-adjudicação de uma rodada humana."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=ROOT / "independent_review" / "returns" / "round_002.jsonl",
    )
    args = parser.parse_args()
    manifest = json.loads((ROOT / "independent_review/selection_manifest.json").read_text("utf-8"))
    dataset_path = ROOT / "items.jsonl"
    normalized = dataset_path.read_bytes().replace(b"\r\n", b"\n")
    if hashlib.sha256(normalized).hexdigest() != manifest["dataset_sha256"]:
        raise EndToEndDatasetError(
            "Snapshot primário mudou; reconciliar a seleção antes da análise."
        )
    by_id = {
        item.item_id: item for item in load_end_to_end_items(dataset_path, require_reviewed=True)
    }
    expected = {entry["task_id"]: by_id[entry["item_id"]] for entry in manifest["mapping"]}
    if any(item.primary_label is None for item in expected.values()):
        raise EndToEndDatasetError("Rótulos primários originais ausentes.")
    primary = {task: item.primary_label for task, item in expected.items()}
    responses = load_annotation_responses(args.path, expected_tasks=expected)
    result = compute_annotation_agreement(primary, responses)
    result["round_id"] = responses[0].round_id
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
