"""Confere a adjudicação v2 em memória, sem publicar ou executar modelos."""

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
    EndToEndDatasetError,
    load_end_to_end_items,
    serialize_end_to_end_items,
    summarize_end_to_end_items,
)
from immunocheck.ingestion.corpus_versioning import load_published_corpus

REPOSITORY = Path(__file__).resolve().parents[1]
BASE = REPOSITORY / "evaluation" / "refinement_v2" / "calibration"
INDEPENDENT = BASE / "independent_review"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def inspect(path: Path) -> dict[str, object]:
    selection = json.loads((INDEPENDENT / "selection_manifest.json").read_text("utf-8"))
    receipt = json.loads((INDEPENDENT / "review_receipt.json").read_text("utf-8"))
    primary_path = BASE / "reviewed_items.jsonl"
    if normalized_sha256(primary_path) != selection["reviewed_dataset_sha256"]:
        raise EndToEndDatasetError("Snapshot primário da calibração foi alterado.")
    for entry in receipt["files"]:
        target = (INDEPENDENT / entry["path"]).resolve()
        if not target.is_relative_to(INDEPENDENT.resolve()):
            raise EndToEndDatasetError("Caminho fora do pacote de revisão.")
        if normalized_sha256(target) != entry["sha256"]:
            raise EndToEndDatasetError("Artefato arquivado foi alterado: " + entry["path"])

    items = load_end_to_end_items(primary_path, require_reviewed=True)
    by_id = {item.item_id: item for item in items}
    expected = {entry["task_id"]: by_id[entry["item_id"]] for entry in selection["mapping"]}
    responses = load_annotation_responses(
        INDEPENDENT / "returns" / "round_001.jsonl", expected_tasks=expected
    )
    adjudication_tasks = {
        task_id: expected[task_id].item_id for task_id in receipt["adjudication_task_ids"]
    }
    decisions = load_adjudication_decisions(
        path,
        expected_tasks=adjudication_tasks,
        expected_claims={task_id: expected[task_id].claim for task_id in adjudication_tasks},
    )
    pending = pending_decision_ids(decisions)
    agreement = compute_annotation_agreement(
        {task_id: item.primary_label for task_id, item in expected.items()}, responses
    )
    report: dict[str, object] = {
        "mode": "read_only",
        "secondary_annotation_accepted": True,
        "pre_adjudication_agreement": agreement,
        "adjudication_tasks": len(decisions),
        "pending_task_ids": list(pending),
        "candidate_created": False,
        "dataset_changed": False,
        "pipeline_predictions_loaded": 0,
        "holdout_created": False,
    }
    if pending:
        return report

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
    report.update(
        {
            "candidate_created": True,
            "candidate_sha256": hashlib.sha256(
                serialize_end_to_end_items(candidate.items).encode("utf-8")
            ).hexdigest(),
            "candidate_summary": asdict(summarize_end_to_end_items(candidate.items)),
            "excluded_item_ids": list(candidate.excluded_item_ids),
            "calibration_structurally_valid": len(candidate.items) == 48,
            "benchmark_readiness_not_applicable": candidate.readiness_error,
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita a adjudicação da calibração v2.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=INDEPENDENT / "adjudication" / "TASKS.md",
    )
    args = parser.parse_args()
    try:
        report = inspect(args.path)
    except (EndToEndDatasetError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"mode": "read_only", "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from exc
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
