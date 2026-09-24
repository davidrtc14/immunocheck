"""Consolida uma correção pontual sem alterar o snapshot de calibração."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from immunocheck.evaluation.annotation_agreement import (
    AnnotationResponse,
    compute_annotation_agreement,
)
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_annotation_return import (
    inspect_refinement_annotation_return,
    inspect_refinement_correction,
    merge_refinement_correction,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evaluation" / "refinement_v2" / "calibration"
INDEPENDENT = BASE / "independent_review"
ORIGINAL = INDEPENDENT / "attempts" / "ATTEMPT_002_RETURN.md"
CORRECTION_ARCHIVE = INDEPENDENT / "attempts" / "ATTEMPT_002_CORRECTION_RETURN.md"
CORRECTED_TASK_ID = "ref2-annotation-010"
ROUND_ID = "ref2-round-001"


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(normalized_text(path).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, value: object) -> None:
    _write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def consolidate(correction_path: Path, *, write: bool) -> dict[str, object]:
    items = {
        item.item_id: item
        for item in load_end_to_end_items(BASE / "reviewed_items.jsonl", require_reviewed=True)
    }
    selection = json.loads((INDEPENDENT / "selection_manifest.json").read_text("utf-8"))
    mapping = {entry["task_id"]: entry for entry in selection["mapping"]}
    expected = {task_id: items[entry["item_id"]] for task_id, entry in mapping.items()}

    original = inspect_refinement_annotation_return(
        ORIGINAL.read_text(encoding="utf-8-sig"), expected_tasks=expected
    )
    correction_text = normalized_text(correction_path)
    correction = inspect_refinement_correction(
        correction_text,
        expected_task_id=CORRECTED_TASK_ID,
        expected_task=expected[CORRECTED_TASK_ID],
        expected_reviewer="rv0067",
    )
    merged = merge_refinement_correction(original, correction, expected_tasks=expected)
    assert merged.reviewer and merged.reviewed_at and merged.agreement

    responses = tuple(
        AnnotationResponse(
            round_id=ROUND_ID,
            task_id=response.task_id,
            item_id=mapping[response.task_id]["item_id"],
            claim=response.claim,
            second_label=response.second_label,
            rationale=response.rationale,
            sources_consulted=response.sources_consulted,
            uncertainty=response.uncertainty,
            reviewer=merged.reviewer,
            reviewed_at=(
                correction.corrected_at
                if response.task_id == CORRECTED_TASK_ID
                else original.reviewed_at
            ),
        )
        for response in merged.responses
    )
    primary = {task_id: item.primary_label for task_id, item in expected.items()}
    agreement = compute_annotation_agreement(primary, responses)
    report: dict[str, object] = {
        "correction_accepted": True,
        "reviewer": merged.reviewer,
        "correction_date": correction.corrected_at,
        "corrected_task_id": CORRECTED_TASK_ID,
        "agreement": agreement,
    }
    if not write:
        return report

    _write_text(CORRECTION_ARCHIVE, correction_text)
    correction_receipt = {
        "schema_version": 1,
        "received_at": correction.corrected_at,
        "source_normalized_sha256": normalized_sha256(CORRECTION_ARCHIVE),
        "raw_return_versioned": True,
        "raw_return_path": CORRECTION_ARCHIVE.name,
        "reviewer_code": merged.reviewer,
        "corrected_task_id": CORRECTED_TASK_ID,
        "claim_integrity": "exact_match",
        "second_label": correction.response.second_label.value,
        "accepted": True,
        "base_return_normalized_sha256": normalized_sha256(ORIGINAL),
    }
    correction_receipt_path = INDEPENDENT / "attempts" / "attempt_002_correction_receipt.json"
    _write_json(correction_receipt_path, correction_receipt)

    returns_dir = INDEPENDENT / "returns"
    round_path = returns_dir / "round_001.jsonl"
    lines = []
    for response in responses:
        value = {"schema_version": 1, **asdict(response)}
        value["second_label"] = response.second_label.value
        lines.append(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    _write_text(round_path, "\n".join(lines) + "\n")
    agreement_path = returns_dir / "agreement_round_001.json"
    _write_json(agreement_path, agreement)

    tracked = (
        ORIGINAL,
        CORRECTION_ARCHIVE,
        correction_receipt_path,
        round_path,
        agreement_path,
        INDEPENDENT / "adjudication" / "TASKS.md",
    )
    receipt = {
        "schema_version": 1,
        "purpose": "refinement_v2_independent_annotation_pending_adjudication",
        "reviewer": merged.reviewer,
        "reviewer_identity_certified": False,
        "independence": "self_declared",
        "round_id": ROUND_ID,
        "original_reviewed_at": original.reviewed_at,
        "correction_reviewed_at": correction.corrected_at,
        "secondary_annotation_accepted": True,
        "response_count": len(responses),
        "agreement_count": agreement["agreement_count"],
        "observed_agreement": agreement["observed_agreement"],
        "cohens_kappa": agreement["cohens_kappa"],
        "adjudication_completed": False,
        "adjudication_task_ids": agreement["disagreement_task_ids"],
        "dataset_changed": False,
        "pipeline_predictions_loaded": 0,
        "hash_normalization": "UTF-8, CRLF normalized to LF, no BOM",
        "files": [
            {
                "path": str(path.relative_to(INDEPENDENT)).replace("\\", "/"),
                "sha256": file_sha256(path),
            }
            for path in tracked
        ],
    }
    _write_json(INDEPENDENT / "review_receipt.json", receipt)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida e consolida a correção da segunda anotação da calibração v2."
    )
    parser.add_argument("correction", type=Path)
    parser.add_argument("--write", action="store_true", help="Publica os artefatos validados.")
    args = parser.parse_args()
    print(json.dumps(consolidate(args.correction, write=args.write), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
