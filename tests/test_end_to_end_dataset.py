from __future__ import annotations

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
