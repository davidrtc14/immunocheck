"""Materializa a calibração v2 adjudicada sem alterar o snapshot primário."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from immunocheck.evaluation.adjudication import (
    assemble_adjudication_candidate,
    load_adjudication_decisions,
    pending_decision_ids,
)
from immunocheck.evaluation.annotation_agreement import (
    compute_annotation_agreement,
    load_annotation_responses,
)
from immunocheck.evaluation.end_to_end import (
    DatasetStatus,
    EndToEndDatasetError,
    load_end_to_end_items,
    serialize_end_to_end_items,
    summarize_end_to_end_items,
)
from immunocheck.evaluation.refinement_calibration import (
    load_family_ids,
    validate_refinement_calibration,
)
from immunocheck.ingestion.corpus_versioning import load_published_corpus

REPOSITORY = Path(__file__).resolve().parents[1]
REFINEMENT = REPOSITORY / "evaluation" / "refinement_v2"
BASE = REFINEMENT / "calibration"
INDEPENDENT = BASE / "independent_review"
PRIMARY = BASE / "reviewed_items.jsonl"
OUTPUT = BASE / "adjudicated_items.jsonl"
RECEIPT = INDEPENDENT / "adjudication" / "adjudication_receipt.json"
FROZEN_FAMILIES = REFINEMENT / "FROZEN_TEST_FAMILIES.txt"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def finalize(decisions_path: Path, *, write: bool) -> dict[str, object]:
    decisions_path = decisions_path.resolve()
    if not decisions_path.is_relative_to(INDEPENDENT.resolve()):
        raise EndToEndDatasetError("A decisão deve permanecer dentro do pacote de revisão.")
    selection = json.loads((INDEPENDENT / "selection_manifest.json").read_text("utf-8"))
    review_receipt = json.loads((INDEPENDENT / "review_receipt.json").read_text("utf-8"))
    if normalized_sha256(PRIMARY) != selection["reviewed_dataset_sha256"]:
        raise EndToEndDatasetError("Snapshot primário da calibração foi alterado.")
    for entry in review_receipt["files"]:
        target = (INDEPENDENT / entry["path"]).resolve()
        if not target.is_relative_to(INDEPENDENT.resolve()):
            raise EndToEndDatasetError("Caminho fora do pacote de revisão.")
        if normalized_sha256(target) != entry["sha256"]:
            raise EndToEndDatasetError("Artefato arquivado foi alterado: " + entry["path"])

    items = load_end_to_end_items(PRIMARY, require_reviewed=True)
    by_id = {item.item_id: item for item in items}
    expected = {entry["task_id"]: by_id[entry["item_id"]] for entry in selection["mapping"]}
    responses = load_annotation_responses(
        INDEPENDENT / "returns" / "round_001.jsonl", expected_tasks=expected
    )
    adjudication_tasks = {
        task_id: expected[task_id].item_id for task_id in review_receipt["adjudication_task_ids"]
    }
    decisions = load_adjudication_decisions(
        decisions_path,
        expected_tasks=adjudication_tasks,
        expected_claims={task_id: expected[task_id].claim for task_id in adjudication_tasks},
    )
    pending = pending_decision_ids(decisions)
    if pending:
        raise EndToEndDatasetError("Decisões humanas pendentes: " + ", ".join(pending))

    corpus = load_published_corpus(
        manifest_path=REPOSITORY / "corpus" / "processed" / "manifest.json",
        chunks_path=REPOSITORY / "corpus" / "processed" / "chunks.jsonl",
    )
    candidate = assemble_adjudication_candidate(
        items,
        responses,
        decisions,
        expected_tasks=adjudication_tasks,
        valid_chunk_ids={chunk["chunk_id"] for chunk in corpus.chunks},
    )
    frozen_families = load_family_ids(FROZEN_FAMILIES.read_text("utf-8").splitlines())
    calibration = validate_refinement_calibration(
        candidate.items,
        frozen_test_families=frozen_families,
        expected_status=DatasetStatus.REVIEWED,
    )
    serialized = serialize_end_to_end_items(candidate.items)
    candidate_sha256 = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    agreement = compute_annotation_agreement(
        {task_id: item.primary_label for task_id, item in expected.items()}, responses
    )
    report: dict[str, object] = {
        "mode": "write" if write else "dry_run",
        "candidate_sha256": candidate_sha256,
        "summary": asdict(summarize_end_to_end_items(candidate.items)),
        "calibration": asdict(calibration),
        "pre_adjudication_agreement": agreement,
        "adjudication_task_ids": [decision.task_id for decision in decisions],
        "final_labels": {
            decision.task_id: decision.final_label.value
            for decision in decisions
            if decision.final_label is not None
        },
        "primary_snapshot_changed": False,
        "holdout_created": False,
        "pipeline_predictions_loaded": 0,
    }
    if not write:
        return report

    OUTPUT.write_text(serialized, encoding="utf-8", newline="\n")
    receipt = {
        "schema_version": 1,
        "purpose": "refinement_v2_completed_human_adjudication",
        "completed_at": "2026-09-26",
        "approval_source": "explicit_project_author_approval",
        "adjudicator_codes": sorted({decision.reviewer for decision in decisions}),
        "decision_count": len(decisions),
        "decision_file": str(decisions_path.relative_to(INDEPENDENT)).replace("\\", "/"),
        "decision_file_sha256": normalized_sha256(decisions_path),
        "primary_snapshot_sha256": normalized_sha256(PRIMARY),
        "adjudicated_snapshot_path": str(OUTPUT.relative_to(BASE)).replace("\\", "/"),
        "adjudicated_snapshot_sha256": candidate_sha256,
        "secondary_reviewed_items": sum(
            item.second_reviewer is not None for item in candidate.items
        ),
        "adjudicated_items": sum(item.adjudicator is not None for item in candidate.items),
        "pre_adjudication_agreement": agreement,
        "final_labels": report["final_labels"],
        "excluded_item_ids": list(candidate.excluded_item_ids),
        "primary_snapshot_changed": False,
        "holdout_created": False,
        "pipeline_predictions_loaded": 0,
    }
    RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Finaliza a calibração v2 adjudicada.")
    parser.add_argument("decisions", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        report = finalize(args.decisions, write=args.write)
    except (EndToEndDatasetError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from exc
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
