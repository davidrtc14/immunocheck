"""Auditoria local somente leitura: nenhum arquivo, banco ou modelo é alterado."""

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
    validate_dataset_ready,
)
from immunocheck.evaluation.split_rebalance import class_split_counts, propose_minimal_family_swap
from immunocheck.ingestion.corpus_versioning import CorpusVersioningError, load_published_corpus

REPOSITORY = Path(__file__).resolve().parents[1]
ROOT = REPOSITORY / "evaluation/end_to_end"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def inspect_adjudication(path: Path, *, root: Path = ROOT) -> dict[str, object]:
    independent = root / "independent_review"
    selection = json.loads((independent / "selection_manifest.json").read_text("utf-8"))
    receipt = json.loads((independent / "review_receipt.json").read_text("utf-8"))
    if normalized_sha256(root / "items.jsonl") != selection["dataset_sha256"]:
        raise EndToEndDatasetError("Snapshot primário alterado; reconciliar antes da incorporação.")
    for entry in receipt["files"]:
        # O formato do recibo é conferido nos testes e não autoriza leitura fora do pacote.
        relative = Path(entry["path"])
        target = (independent / relative).resolve()
        if not target.is_relative_to(independent.resolve()):
            raise EndToEndDatasetError("Caminho de recibo fora do pacote.")
        if normalized_sha256(target) != entry["sha256"]:
            raise EndToEndDatasetError("Artefato arquivado alterado: " + str(relative))
    items = load_end_to_end_items(root / "items.jsonl", require_reviewed=True)
    by_id = {item.item_id: item for item in items}
    expected = {entry["task_id"]: by_id[entry["item_id"]] for entry in selection["mapping"]}
    if len(expected) != len(selection["mapping"]):
        raise EndToEndDatasetError("Seleção duplicada.")
    expected_adjudication = {
        task: expected[task].item_id for task in receipt["adjudication_task_ids"]
    }
    responses = load_annotation_responses(
        independent / "returns/round_002.jsonl", expected_tasks=expected
    )
    decisions = load_adjudication_decisions(
        path,
        expected_tasks=expected_adjudication,
        expected_claims={task: expected[task].claim for task in expected_adjudication},
    )
    primary = {task: item.primary_label for task, item in expected.items()}
    pending = pending_decision_ids(decisions)
    report: dict[str, object] = {
        "mode": "read_only",
        "dataset_snapshot_sha256": selection["dataset_sha256"],
        "secondary_responses_received": len(responses),
        "secondary_responses_applied_to_authoritative_items": sum(
            item.second_reviewer is not None for item in items
        ),
        "adjudication_tasks": len(decisions),
        "pending_task_ids": list(pending),
        "pre_adjudication_agreement": compute_annotation_agreement(primary, responses),
        "candidate_created": False,
        "test_frozen": False,
        "human_gates_not_certified_by_software": [
            "pertinência semântica das evidências de todos os itens",
            "ausência de vazamento semântico entre famílias e splits",
            "competência, independência e procedimento declarados pelos anotadores",
            "reconciliação de correções/exclusões e autorização final de congelamento",
        ],
    }
    if pending:
        return report
    corpus_root = root.parents[1] / "corpus/processed"
    corpus = load_published_corpus(
        manifest_path=corpus_root / "manifest.json", chunks_path=corpus_root / "chunks.jsonl"
    )
    if corpus.manifest["corpus_version"] != selection["corpus_version"]:
        raise EndToEndDatasetError("Versão do corpus mudou desde a seleção.")
    chunks = {chunk["chunk_id"] for chunk in corpus.chunks}
    candidate = assemble_adjudication_candidate(
        items,
        responses,
        decisions,
        expected_tasks=expected_adjudication,
        valid_chunk_ids=chunks,
    )
    report.update(
        {
            "candidate_created": True,
            "candidate_summary": asdict(summarize_end_to_end_items(candidate.items)),
            "candidate_sha256": hashlib.sha256(
                serialize_end_to_end_items(candidate.items).encode("utf-8")
            ).hexdigest(),
            "excluded_item_ids": list(candidate.excluded_item_ids),
            "structurally_ready": candidate.structurally_ready,
            "readiness_error": candidate.readiness_error,
            "class_split_counts": class_split_counts(candidate.items),
            "secondary_review_class_split_counts": class_split_counts(
                tuple(item for item in candidate.items if item.second_reviewer is not None)
            ),
        }
    )
    if candidate.readiness_error == "O split deve ser estratificado em 60%/40% por classe.":
        plan = propose_minimal_family_swap(candidate.items, seed=20260916)
        ready_summary = validate_dataset_ready(plan.items)
        report["minimal_family_rebalance"] = {
            "seed": 20260916,
            "selection_rule": (
                "menor numero de itens movidos; desempate SHA-256 da semente e familias"
            ),
            "uses_system_predictions": False,
            "development_to_test": plan.development_to_test,
            "test_to_development": plan.test_to_development,
            "moved_item_ids": list(plan.moved_item_ids),
            "development_targets": plan.development_targets,
            "class_split_counts": class_split_counts(plan.items),
            "secondary_review_class_split_counts": class_split_counts(
                tuple(item for item in plan.items if item.second_reviewer is not None)
            ),
            "structurally_ready": True,
            "summary": asdict(ready_summary),
            "candidate_sha256": hashlib.sha256(
                serialize_end_to_end_items(plan.items).encode("utf-8")
            ).hexdigest(),
            "test_frozen": False,
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Conferência em lote de adjudicação humana.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=ROOT / "independent_review/adjudication/TASKS.md",
    )
    args = parser.parse_args()
    try:
        report = inspect_adjudication(args.path)
    except (
        EndToEndDatasetError,
        CorpusVersioningError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        print(json.dumps({"mode": "read_only", "error": str(exc), "test_frozen": False}))
        raise SystemExit(2) from exc
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
