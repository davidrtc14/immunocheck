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
