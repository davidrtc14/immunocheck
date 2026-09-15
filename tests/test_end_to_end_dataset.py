from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    load_end_to_end_items,
    summarize_end_to_end_items,
    validate_dataset_ready,
)


def item(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "item_id": "e2e-0001",
        "claim": "A vacina está indicada para este grupo.",
        "label": "SUPPORTED",
        "topic": "normas_e_calendarios",
        "split": "development",
        "status": "reviewed",
        "atomic": True,
        "evidence_chunk_ids": ["chunk-1"],
        "rationale": "O trecho apresenta diretamente a indicação.",
        "origin_type": "official_document",
        "origin_reference": "documento-1",
        "reviewer": "anotador-1",
        "reviewed_at": "2026-09-01",
        "second_reviewer": None,
        "second_label": None,
        "second_reviewed_at": None,
        "adjudicator": None,
        "adjudicated_at": None,
        "notes": None,
        "claim_family": "familia-1",
    }
    value.update(overrides)
    return value


def write_items(path: Path, *items: dict[str, object]) -> None:
    path.write_text(
        "".join(json.dumps(value, ensure_ascii=False) + "\n" for value in items),
        encoding="utf-8",
    )


def test_loader_accepts_reviewed_atomic_item_with_valid_evidence(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, item())

    result = load_end_to_end_items(
        path,
        valid_chunk_ids={"chunk-1"},
        require_reviewed=True,
    )

    assert result[0].label is Verdict.SUPPORTED
    assert result[0].split is DatasetSplit.DEVELOPMENT


def test_loader_rejects_conclusive_item_without_evidence(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, item(evidence_chunk_ids=[]))

    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_loader_rejects_insufficient_item_with_conclusive_evidence(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, item(label="INSUFFICIENT_EVIDENCE"))

    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_loader_rejects_disagreement_without_adjudication(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            second_reviewer="anotador-2",
            second_label="REFUTED",
            second_reviewed_at="2026-09-02",
        ),
    )

    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_summary_reports_second_review_fraction(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            second_reviewer="anotador-2",
            second_label="SUPPORTED",
            second_reviewed_at="2026-09-02",
        ),
    )
    items = load_end_to_end_items(path)

    summary = summarize_end_to_end_items(items)

    assert summary.second_review_fraction == 1.0
    assert summary.labels == {"SUPPORTED": 1}


def test_ready_validator_enforces_minimum_size(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            second_reviewer="anotador-2",
            second_label="SUPPORTED",
            second_reviewed_at="2026-09-02",
        ),
    )
    with pytest.raises(EndToEndDatasetError, match="mínimo documentado"):
        validate_dataset_ready(load_end_to_end_items(path))


def balanced_items() -> list[dict[str, object]]:
    return [
        item(
            item_id=f"{label.value}-{index}",
            claim=f"Proposição de teste {label.value} {index}.",
            label=label.value,
            primary_label=label.value,
            evidence_chunk_ids=[] if label is Verdict.INSUFFICIENT_EVIDENCE else ["chunk-1"],
            split="development" if index < 15 else "test",
            claim_family=f"familia-{label.value}-{index}",
            second_reviewer="anotador-2",
            second_label=label.value,
            second_reviewed_at="2026-09-02",
        )
        for label in Verdict
        for index in range(25)
    ]


def test_ready_validator_accepts_balanced_stratified_dataset(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, *balanced_items())
    assert validate_dataset_ready(load_end_to_end_items(path)).total == 100


def test_ready_validator_rejects_class_below_minimum(tmp_path: Path) -> None:
    values = balanced_items()
    values[0].update(label="REFUTED", primary_label="REFUTED", second_label="REFUTED")
    path = tmp_path / "items.jsonl"
    write_items(path, *values)
    with pytest.raises(EndToEndDatasetError, match="25 itens"):
        validate_dataset_ready(load_end_to_end_items(path))


def test_ready_validator_rejects_unstratified_split(tmp_path: Path) -> None:
    values = balanced_items()
    values[0]["split"] = "test"
    path = tmp_path / "items.jsonl"
    write_items(path, *values)
    with pytest.raises(EndToEndDatasetError, match="60%/40%"):
        validate_dataset_ready(load_end_to_end_items(path))


def test_ready_validator_rejects_missing_family(tmp_path: Path) -> None:
    values = balanced_items()
    values[0]["claim_family"] = None
    path = tmp_path / "items.jsonl"
    write_items(path, *values)
    with pytest.raises(EndToEndDatasetError, match="família"):
        validate_dataset_ready(load_end_to_end_items(path))


def test_loader_rejects_family_leakage_between_splits(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, item(), item(item_id="e2e-2", claim="Outra paráfrase.", split="test"))
    with pytest.raises(EndToEndDatasetError, match="família"):
        load_end_to_end_items(path)


def test_loader_rejects_same_person_as_second_reviewer(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            second_reviewer="ANOTADOR-1", second_label="SUPPORTED", second_reviewed_at="2026-09-02"
        ),
    )
    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_ready_validator_requires_original_primary_labels(tmp_path: Path) -> None:
    values = balanced_items()
    values[0]["primary_label"] = None
    path = tmp_path / "items.jsonl"
    write_items(path, *values)
    with pytest.raises(EndToEndDatasetError, match="primeiro anotador"):
        validate_dataset_ready(load_end_to_end_items(path))


def test_adjudication_preserves_original_labels_when_second_label_wins(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            primary_label="SUPPORTED",
            second_reviewer="anotador-2",
            second_label="REFUTED",
            second_reviewed_at="2026-09-02",
            label="REFUTED",
            adjudicator="adjudicador-1",
            adjudicated_at="2026-09-03",
        ),
    )
    result = load_end_to_end_items(path)[0]
    assert result.primary_label is Verdict.SUPPORTED
    assert result.second_label is result.label is Verdict.REFUTED


def test_loader_rejects_final_label_changed_without_adjudication(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(path, item(primary_label="REFUTED"))
    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_loader_rejects_second_annotation_on_draft(tmp_path: Path) -> None:
    path = tmp_path / "items.jsonl"
    write_items(
        path,
        item(
            status="draft",
            reviewer=None,
            reviewed_at=None,
            rationale=None,
            second_reviewer="anotador-2",
            second_label="SUPPORTED",
            second_reviewed_at="2026-09-02",
        ),
    )
    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_end_to_end_items(path)


def test_candidate_batch_remains_unreviewed_and_development_only() -> None:
    path = Path(__file__).parents[1] / "evaluation/end_to_end/batches/batch_001.jsonl"
    items = load_end_to_end_items(path)
    summary = summarize_end_to_end_items(items)
    assert summary.total == 12
    assert summary.reviewed == summary.second_reviewed == 0
    assert summary.splits == {"development": 12}
    assert summary.labels == {verdict.value: 3 for verdict in Verdict}
    assert all(entry.primary_label is None and entry.reviewer is None for entry in items)
    with pytest.raises(EndToEndDatasetError, match="sem revisão humana"):
        load_end_to_end_items(path, require_reviewed=True)


def test_approved_batch_has_assisted_primary_review_without_second_annotation() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    candidates = load_end_to_end_items(root / "batches/batch_001.jsonl")
    reviewed = load_end_to_end_items(root / "items.jsonl", require_reviewed=True)
    summary = summarize_end_to_end_items(reviewed)
    assert summary.total == summary.reviewed == 12
    assert summary.second_reviewed == 0
    for candidate, approved in zip(candidates, reviewed, strict=True):
        assert candidate.item_id == approved.item_id
        assert candidate.claim == approved.claim
        assert candidate.evidence_chunk_ids == approved.evidence_chunk_ids
        assert candidate.claim_family == approved.claim_family
        assert candidate.label is approved.label is approved.primary_label
        assert approved.reviewer == "project_author"
        assert approved.reviewed_at == "2026-09-15"
        assert approved.rationale and approved.second_label is None
    with pytest.raises(EndToEndDatasetError, match="mínimo documentado"):
        validate_dataset_ready(reviewed)


def test_second_candidate_batch_is_pending_review() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    candidates = load_end_to_end_items(root / "batches/batch_002.jsonl")
    summary = summarize_end_to_end_items(candidates)
    assert summary.total == 12
    assert summary.reviewed == summary.second_reviewed == 0
    assert summary.splits == {"development": 12}
    assert summary.labels == {verdict.value: 3 for verdict in Verdict}
    assert all(entry.primary_label is None for entry in candidates)
    with pytest.raises(EndToEndDatasetError, match="sem revisão humana"):
        load_end_to_end_items(root / "batches/batch_002.jsonl", require_reviewed=True)


def test_reviewed_and_pending_pools_have_distinct_ids_and_no_split_leakage(tmp_path: Path) -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    merged = tmp_path / "pool.jsonl"
    merged.write_text(
        (root / "items.jsonl").read_text(encoding="utf-8")
        + (root / "batches/batch_002.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    summary = summarize_end_to_end_items(load_end_to_end_items(merged))
    assert summary.total == 24 and summary.reviewed == 12


@pytest.mark.parametrize("batch_number", range(3, 13))
def test_all_remaining_batches_are_drafts_with_stratified_proposals(batch_number: int) -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    items = load_end_to_end_items(root / f"batches/batch_{batch_number:03d}.jsonl")
    summary = summarize_end_to_end_items(items)
    expected_count = 12 if batch_number <= 8 else 16
    expected_split = "development" if batch_number <= 8 else "test"
    assert summary.total == expected_count
    assert summary.reviewed == summary.second_reviewed == 0
    assert summary.splits == {expected_split: expected_count}
    assert summary.labels == {verdict.value: expected_count // 4 for verdict in Verdict}
    assert all(entry.primary_label is None and entry.reviewer is None for entry in items)
    for entry in items:
        if entry.label is Verdict.INSUFFICIENT_EVIDENCE:
            assert not entry.evidence_chunk_ids
            assert entry.origin_type == "synthetic_scenario"
        else:
            assert entry.evidence_chunk_ids and entry.origin_reference


def test_complete_review_pool_is_not_an_approved_or_frozen_dataset() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    path = root / "review_pool.jsonl"
    items = load_end_to_end_items(path)
    summary = summarize_end_to_end_items(items)
    assert summary.total == 160
    assert summary.reviewed == 12 and summary.second_reviewed == 0
    assert summary.labels == {verdict.value: 40 for verdict in Verdict}
    assert summary.splits == {"development": 96, "test": 64}
    for verdict in Verdict:
        assert (
            sum(
                entry.label is verdict and entry.split is DatasetSplit.DEVELOPMENT
                for entry in items
            )
            == 24
        )
    with pytest.raises(EndToEndDatasetError, match="revisão humana"):
        validate_dataset_ready(items)


def test_review_pool_matches_approved_items_and_pending_batch_sources() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    expected = list(load_end_to_end_items(root / "items.jsonl", require_reviewed=True))
    for number in range(2, 13):
        expected.extend(load_end_to_end_items(root / f"batches/batch_{number:03d}.jsonl"))
    assert load_end_to_end_items(root / "review_pool.jsonl") == tuple(expected)


def test_review_manifest_matches_files_and_does_not_declare_test_frozen() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    manifest = json.loads((root / "review_pool_manifest.json").read_text(encoding="utf-8"))
    assert manifest["test_frozen"] is False
    assert manifest["total"] == 160 and manifest["pending"] == 148
    assert manifest["primary_reviewed"] == 12 and manifest["second_reviewed"] == 0
    assert len(manifest["files"]) == 14
    for record in manifest["files"]:
        content = (root / record["path"]).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest() == record["sha256"]
