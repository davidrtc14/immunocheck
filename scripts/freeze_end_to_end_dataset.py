"""Materializa o benchmark aprovado e publica o manifesto por último."""

from __future__ import annotations

import argparse
import json
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
from immunocheck.evaluation.benchmark_freeze import (
    build_freeze_manifest,
    normalized_markdown_bytes,
    serialize_freeze_manifest,
    sha256_bytes,
    validate_freeze_manifest,
)
from immunocheck.evaluation.end_to_end import (
    EndToEndDatasetError,
    load_end_to_end_items,
    serialize_end_to_end_items,
    validate_dataset_ready,
)
from immunocheck.evaluation.split_rebalance import propose_minimal_family_swap
from immunocheck.ingestion.corpus_versioning import load_published_corpus
from immunocheck.retrieval.dense import BGE_M3_MODEL, BGE_M3_REVISION

REPOSITORY = Path(__file__).resolve().parents[1]
ROOT = REPOSITORY / "evaluation/end_to_end"
DECISIONS_ARCHIVE = "independent_review/adjudication/DECISIONS_round_002.md"
AUDIT_ARCHIVE = "independent_review/adjudication/AUDIT_round_002.md"
REBALANCE_SEED = 20260916
EXPECTED_DEVELOPMENT_TO_TEST = "art_fertility_scope"
EXPECTED_TEST_TO_DEVELOPMENT = "vaccination_coverage_relative_increment"


def normalized_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def prepare_freeze(
    decisions_path: Path,
    audit_path: Path,
    *,
    root: Path = ROOT,
    frozen_at: str,
) -> tuple[bytes, bytes, bytes, dict[str, object]]:
    independent = root / "independent_review"
    selection = json.loads((independent / "selection_manifest.json").read_text("utf-8"))
    receipt = json.loads((independent / "review_receipt.json").read_text("utf-8"))
    primary_path = root / "review_pool.jsonl"
    if normalized_sha256(primary_path) != selection["dataset_sha256"]:
        raise EndToEndDatasetError("Snapshot primário preservado diverge da seleção.")
    for record in receipt["files"]:
        relative = Path(record["path"])
        target = (independent / relative).resolve()
        if not target.is_relative_to(independent.resolve()):
            raise EndToEndDatasetError("Caminho histórico fora do pacote independente.")
        if normalized_sha256(target) != record["sha256"]:
            raise EndToEndDatasetError("Artefato histórico alterado: " + str(relative))

    primary = load_end_to_end_items(primary_path, require_reviewed=True)
    by_id = {item.item_id: item for item in primary}
    expected = {entry["task_id"]: by_id[entry["item_id"]] for entry in selection["mapping"]}
    expected_adjudication = {
        task: expected[task].item_id for task in receipt["adjudication_task_ids"]
    }
    responses = load_annotation_responses(
        independent / "returns/round_002.jsonl", expected_tasks=expected
    )
    decisions = load_adjudication_decisions(
        decisions_path,
        expected_tasks=expected_adjudication,
        expected_claims={task: expected[task].claim for task in expected_adjudication},
    )
    pending = pending_decision_ids(decisions)
    if pending:
        raise EndToEndDatasetError("Decisões pendentes: " + ", ".join(pending))

    corpus_root = root.parents[1] / "corpus/processed"
    corpus = load_published_corpus(
        manifest_path=corpus_root / "manifest.json", chunks_path=corpus_root / "chunks.jsonl"
    )
    if corpus.manifest["corpus_version"] != selection["corpus_version"]:
        raise EndToEndDatasetError("Versão do corpus mudou desde a seleção.")
    candidate = assemble_adjudication_candidate(
        primary,
        responses,
        decisions,
        expected_tasks=expected_adjudication,
        valid_chunk_ids={chunk["chunk_id"] for chunk in corpus.chunks},
    )
    if candidate.excluded_item_ids:
        raise EndToEndDatasetError("O congelamento aprovado não inclui exclusões.")
    plan = propose_minimal_family_swap(candidate.items, seed=REBALANCE_SEED)
    if (
        plan.development_to_test != EXPECTED_DEVELOPMENT_TO_TEST
        or plan.test_to_development != EXPECTED_TEST_TO_DEVELOPMENT
    ):
        raise EndToEndDatasetError("A troca calculada diverge daquela autorizada.")
    validate_dataset_ready(plan.items)
    dataset_bytes = serialize_end_to_end_items(plan.items).encode("utf-8")
    decisions_bytes = normalized_markdown_bytes(decisions_path.read_bytes())
    audit_bytes = normalized_markdown_bytes(audit_path.read_bytes())

    file_hashes = {
        "items.jsonl": sha256_bytes(dataset_bytes),
        DECISIONS_ARCHIVE: sha256_bytes(decisions_bytes),
        AUDIT_ARCHIVE: sha256_bytes(audit_bytes),
        "independent_review/returns/round_001.jsonl": normalized_sha256(
            independent / "returns/round_001.jsonl"
        ),
        "independent_review/returns/round_002.jsonl": normalized_sha256(
            independent / "returns/round_002.jsonl"
        ),
        "independent_review/review_receipt.json": normalized_sha256(
            independent / "review_receipt.json"
        ),
        "independent_review/selection_manifest.json": normalized_sha256(
            independent / "selection_manifest.json"
        ),
        "review_pool.jsonl": normalized_sha256(primary_path),
    }
    agreement = compute_annotation_agreement(
        {task: item.primary_label for task, item in expected.items()}, responses
    )
    manifest = build_freeze_manifest(
        plan.items,
        frozen_at=frozen_at,
        corpus_version=str(corpus.manifest["corpus_version"]),
        corpus_chunks_sha256=str(corpus.manifest["chunks_sha256"]),
        source_snapshot_sha256=selection["dataset_sha256"],
        file_hashes=file_hashes,
        rebalance={
            "seed": REBALANCE_SEED,
            "selection_rule": ("minimum_moved_items_then_sha256_seed_and_family_names"),
            "uses_system_predictions": False,
            "development_to_test": plan.development_to_test,
            "test_to_development": plan.test_to_development,
            "moved_item_ids": list(plan.moved_item_ids),
        },
        adjudication={
            "decision_count": len(decisions),
            "disagreement_count": agreement["disagreement_count"],
            "agreement_count": agreement["agreement_count"],
            "cohens_kappa_pre_adjudication": agreement["cohens_kappa"],
            "secondary_reviewed": len(responses),
            "excluded_items": 0,
            "reviewer_code": responses[0].reviewer,
            "identity_and_expertise_certified_by_software": False,
        },
        semantic_audit={
            "method": "normalized_cosine_cross_split_ranking",
            "model": BGE_M3_MODEL,
            "model_revision": BGE_M3_REVISION,
            "dataset_identity_sha256": (
                "88118da91882a6701c9e29abb18bb366ded0336cbb5588b0942ae69338f4d03c"
            ),
            "ranked_pairs_read": 40,
            "maximum_cosine_similarity": 0.7011207342147827,
            "same_fact_target_found_in_ranked_pairs": False,
            "decision_authority": "ai_technical_review_accepted_by_project_author",
            "advisor_review_pending": True,
        },
    )
    return dataset_bytes, decisions_bytes, audit_bytes, manifest


def publish_freeze(
    dataset_bytes: bytes,
    decisions_bytes: bytes,
    audit_bytes: bytes,
    manifest: dict[str, object],
    *,
    root: Path = ROOT,
) -> None:
    manifest_path = root / "freeze_manifest.json"
    if manifest_path.exists():
        raise EndToEndDatasetError("O benchmark já possui manifesto de congelamento.")
    writes = (
        (root / DECISIONS_ARCHIVE, decisions_bytes),
        (root / AUDIT_ARCHIVE, audit_bytes),
        (root / "items.jsonl", dataset_bytes),
        (manifest_path, serialize_freeze_manifest(manifest)),
    )
    for path, content in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(content)
        temporary.replace(path)
    validate_freeze_manifest(root=root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Congela o benchmark fim a fim aprovado.")
    parser.add_argument("decisions", type=Path)
    parser.add_argument("audit", type=Path)
    parser.add_argument("--frozen-at", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        dataset, decisions, audit, manifest = prepare_freeze(
            args.decisions, args.audit, frozen_at=args.frozen_at
        )
        if args.apply:
            publish_freeze(dataset, decisions, audit, manifest)
        print(json.dumps(manifest, ensure_ascii=True, indent=2))
    except (EndToEndDatasetError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"test_frozen": False, "error": str(exc)}, ensure_ascii=True))
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
