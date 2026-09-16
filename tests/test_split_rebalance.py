from __future__ import annotations

from dataclasses import replace

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)
from immunocheck.evaluation.split_rebalance import (
    class_split_counts,
    propose_minimal_family_swap,
)


def item(item_id: str, label: Verdict, split: DatasetSplit, family: str) -> EndToEndItem:
    return EndToEndItem(
        item_id=item_id,
        claim=f"Proposição fictícia {item_id}.",
        label=label,
        topic="fixture",
        split=split,
        status=DatasetStatus.REVIEWED,
        atomic=True,
        evidence_chunk_ids=() if label is Verdict.INSUFFICIENT_EVIDENCE else ("fixture",),
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
        claim_family=family,
        primary_label=label,
    )


def imbalanced_items() -> tuple[EndToEndItem, ...]:
    values = [
        item("dev-special-s", Verdict.SUPPORTED, DatasetSplit.DEVELOPMENT, "dev-special"),
        item("dev-special-r1", Verdict.REFUTED, DatasetSplit.DEVELOPMENT, "dev-special"),
        item("dev-special-r2", Verdict.REFUTED, DatasetSplit.DEVELOPMENT, "dev-special"),
        item(
            "dev-special-i",
            Verdict.INSUFFICIENT_EVIDENCE,
            DatasetSplit.DEVELOPMENT,
            "dev-special",
        ),
        item("test-balanced-s", Verdict.SUPPORTED, DatasetSplit.TEST, "test-balanced"),
        item("test-balanced-r", Verdict.REFUTED, DatasetSplit.TEST, "test-balanced"),
        item("test-balanced-m", Verdict.MISLEADING, DatasetSplit.TEST, "test-balanced"),
        item(
            "test-balanced-i",
            Verdict.INSUFFICIENT_EVIDENCE,
            DatasetSplit.TEST,
            "test-balanced",
        ),
    ]
    # Completa S=10, R=11, M=9, I=10; antes da troca, dev=6/8/4/6.
    total_targets = {
        Verdict.SUPPORTED: 10,
        Verdict.REFUTED: 11,
        Verdict.MISLEADING: 9,
        Verdict.INSUFFICIENT_EVIDENCE: 10,
    }
    development_before = {
        Verdict.SUPPORTED: 6,
        Verdict.REFUTED: 8,
        Verdict.MISLEADING: 4,
        Verdict.INSUFFICIENT_EVIDENCE: 6,
    }
    serial = 0
    for label in Verdict:
        current_development = sum(
            value.label is label and value.split is DatasetSplit.DEVELOPMENT for value in values
        )
        while current_development < development_before[label]:
            serial += 1
            # Uma família comum impede que fillers isolados sejam uma troca válida.
            values.append(
                item(f"dev-fill-{serial}", label, DatasetSplit.DEVELOPMENT, "dev-fill-all")
            )
            current_development += 1
        current_total = sum(value.label is label for value in values)
        while current_total < total_targets[label]:
            serial += 1
            values.append(item(f"test-fill-{serial}", label, DatasetSplit.TEST, "test-fill-all"))
            current_total += 1
    return tuple(values)


def test_minimal_swap_restores_targets_without_splitting_families():
    items = imbalanced_items()
    plan = propose_minimal_family_swap(items, seed=20260916)
    assert plan.development_to_test == "dev-special"
    assert plan.test_to_development == "test-balanced"
    assert len(plan.moved_item_ids) == 8
    assert class_split_counts(plan.items) == {
        "SUPPORTED": {"development": 6, "test": 4},
        "REFUTED": {"development": 7, "test": 4},
        "MISLEADING": {"development": 5, "test": 4},
        "INSUFFICIENT_EVIDENCE": {"development": 6, "test": 4},
    }
    assert all(
        len({value.split for value in plan.items if value.claim_family == family}) == 1
        for family in {value.claim_family for value in plan.items}
    )
    assert all(original.split is DatasetSplit.DEVELOPMENT for original in items[:4])


def test_swap_is_reproducible_for_same_seed():
    items = imbalanced_items()
    assert propose_minimal_family_swap(items, seed=7) == propose_minimal_family_swap(items, seed=7)


def test_refuses_already_balanced_or_split_family():
    items = imbalanced_items()
    plan = propose_minimal_family_swap(items, seed=1)
    with pytest.raises(EndToEndDatasetError, match="já atende"):
        propose_minimal_family_swap(plan.items, seed=1)
    broken = (replace(items[0], split=DatasetSplit.TEST), *items[1:])
    with pytest.raises(EndToEndDatasetError, match="dividida"):
        propose_minimal_family_swap(tuple(broken), seed=1)
