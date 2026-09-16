from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)
from immunocheck.evaluation.lexical_baseline import (
    evaluate_lexical_baseline,
    load_frozen_development_items,
)


def item(group: int, verdict: Verdict) -> EndToEndItem:
    tokens = {
        Verdict.SUPPORTED: "confirmado correto evidência",
        Verdict.REFUTED: "falso contradito incorreto",
        Verdict.MISLEADING: "enganoso omite contexto",
        Verdict.INSUFFICIENT_EVIDENCE: "incerto dados ausentes",
    }
    return EndToEndItem(
        item_id=f"item-{group}-{verdict.value}",
        claim=f"{tokens[verdict]} família {group} vacinação.",
        label=verdict,
        topic="fixture",
        split=DatasetSplit.DEVELOPMENT,
        status=DatasetStatus.REVIEWED,
        atomic=True,
        evidence_chunk_ids=() if verdict is Verdict.INSUFFICIENT_EVIDENCE else ("fixture",),
        rationale="Fixture.",
        origin_type="test_fixture",
        origin_reference=None,
        reviewer="fixture_primary",
        reviewed_at="2026-09-01",
        second_reviewer=None,
        second_label=None,
        second_reviewed_at=None,
        adjudicator=None,
        adjudicated_at=None,
        notes=None,
        claim_family=f"family-{group}",
        primary_label=verdict,
    )


def fixture_items() -> tuple[EndToEndItem, ...]:
    return tuple(item(group, verdict) for group in range(8) for verdict in Verdict)


def test_grouped_baseline_is_deterministic_and_keeps_families_isolated() -> None:
    first = evaluate_lexical_baseline(fixture_items(), folds=4, seed=7, bootstrap_resamples=50)
    second = evaluate_lexical_baseline(fixture_items(), folds=4, seed=7, bootstrap_resamples=50)
    assert first == second
    assert first["test_items_loaded_into_model"] is False
    assert first["metrics"]["macro_f1"] == pytest.approx(1.0)
    for fold in first["fold_records"]:
        assert set(fold["training_families"]).isdisjoint(fold["validation_families"])
    assert first["bootstrap_95_percentile_interval"]["macro_f1"] == {
        "lower": 1.0,
        "median": 1.0,
        "upper": 1.0,
    }


def test_baseline_rejects_any_test_item() -> None:
    values = fixture_items()
    contaminated = (replace(values[0], split=DatasetSplit.TEST), *values[1:])
    with pytest.raises(EndToEndDatasetError, match="itens de teste"):
        evaluate_lexical_baseline(contaminated, folds=4, bootstrap_resamples=10)


def test_real_loader_returns_only_frozen_development_partition() -> None:
    root = Path(__file__).parents[1] / "evaluation/end_to_end"
    values = load_frozen_development_items(root)
    assert len(values) == 96
    assert all(value.split is DatasetSplit.DEVELOPMENT for value in values)
    assert len({value.claim_family for value in values}) == 33
