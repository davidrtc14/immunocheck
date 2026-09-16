from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from immunocheck.evaluation.benchmark_freeze import (
    normalized_markdown_bytes,
    validate_freeze_manifest,
)
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    load_end_to_end_items,
    validate_dataset_ready,
)

ROOT = Path(__file__).parents[1] / "evaluation/end_to_end"


def test_published_freeze_is_ready_and_bound_to_all_records() -> None:
    manifest = validate_freeze_manifest(root=ROOT)
    items = load_end_to_end_items(ROOT / "items.jsonl", require_reviewed=True)
    summary = validate_dataset_ready(items)
    assert manifest["test_frozen"] is True
    assert (
        manifest["frozen_dataset_sha256"]
        == hashlib.sha256(
            normalized_markdown_bytes((ROOT / "items.jsonl").read_bytes())
        ).hexdigest()
    )
    assert summary.total == 160 and summary.second_reviewed == 48
    assert summary.labels == {
        "INSUFFICIENT_EVIDENCE": 40,
        "MISLEADING": 31,
        "REFUTED": 49,
        "SUPPORTED": 40,
    }
    assert manifest["adjudication"]["decision_count"] == 22
    assert manifest["adjudication"]["disagreement_count"] == 16
    assert manifest["rebalance"]["uses_system_predictions"] is False
    assert all(
        item.split is DatasetSplit.TEST
        for item in items
        if item.claim_family == "art_fertility_scope"
    )
    assert all(
        item.split is DatasetSplit.DEVELOPMENT
        for item in items
        if item.claim_family == "vaccination_coverage_relative_increment"
    )


def test_freeze_changes_only_review_and_approved_split_fields() -> None:
    manifest = validate_freeze_manifest(root=ROOT)
    primary = {item.item_id: item for item in load_end_to_end_items(ROOT / "review_pool.jsonl")}
    frozen = {item.item_id: item for item in load_end_to_end_items(ROOT / "items.jsonl")}
    assert primary.keys() == frozen.keys()
    stable_fields = (
        "claim",
        "topic",
        "status",
        "atomic",
        "origin_type",
        "origin_reference",
        "reviewer",
        "reviewed_at",
        "claim_family",
        "primary_label",
    )
    assert all(
        getattr(primary[item_id], field) == getattr(frozen[item_id], field)
        for item_id in primary
        for field in stable_fields
    )
    changed_splits = {
        item_id for item_id in primary if primary[item_id].split is not frozen[item_id].split
    }
    assert changed_splits == set(manifest["rebalance"]["moved_item_ids"])
    changed_labels = {
        item_id for item_id in primary if primary[item_id].label is not frozen[item_id].label
    }
    assert changed_labels == {
        "e2e-0008",
        "e2e-0019",
        "e2e-0020",
        "e2e-0021",
        "e2e-0057",
        "e2e-0092",
        "e2e-0105",
        "e2e-0121",
        "e2e-0155",
    }
    assert sum(item.second_reviewer is not None for item in frozen.values()) == 48
    assert sum(item.adjudicator is not None for item in frozen.values()) == 16


def test_published_human_records_are_deidentified_and_exactly_hashed() -> None:
    manifest = validate_freeze_manifest(root=ROOT)
    records = {record["path"]: record["sha256"] for record in manifest["files"]}
    for relative in (
        "independent_review/adjudication/DECISIONS_round_002.md",
        "independent_review/adjudication/AUDIT_round_002.md",
    ):
        content = (ROOT / relative).read_bytes()
        assert hashlib.sha256(normalized_markdown_bytes(content)).hexdigest() == records[relative]
        text = content.decode("utf-8")
        assert "usr_002-independente" in text
        assert "C:\\Users\\" not in text and "@gmail" not in text.casefold()


def test_freeze_validation_rejects_a_tampered_archived_record(tmp_path: Path) -> None:
    copied = tmp_path / "repo/evaluation/end_to_end"
    shutil.copytree(ROOT, copied)
    source_corpus = ROOT.parents[1] / "corpus/processed"
    target_corpus = copied.parents[1] / "corpus/processed"
    target_corpus.mkdir(parents=True)
    shutil.copy2(source_corpus / "manifest.json", target_corpus / "manifest.json")
    target = copied / "independent_review/adjudication/AUDIT_round_002.md"
    target.write_bytes(target.read_bytes() + b"\n")
    with pytest.raises(EndToEndDatasetError, match="alterado"):
        validate_freeze_manifest(root=copied)


def test_markdown_normalization_is_stable() -> None:
    assert normalized_markdown_bytes(b"\xef\xbb\xbfA\r\nB\rC\n") == b"A\nB\nC\n"
