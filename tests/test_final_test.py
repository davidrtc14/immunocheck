from __future__ import annotations

from dataclasses import replace

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError
from immunocheck.evaluation.final_test import (
    summarize_final_test,
    validate_final_test_checkpoint,
)
from tests.test_lexical_baseline import item


def final_items():
    return tuple(
        replace(
            item(group, verdict),
            split=DatasetSplit.TEST,
            item_id=f"test-{group}-{verdict.value}",
        )
        for group in range(16)
        for verdict in Verdict
    )


def final_records(items):
    return [
        {
            "item_id": current.item_id,
            "claim_family": current.claim_family,
            "expected_label": current.label.value,
            "result": {
                "verdict": current.label.value,
                "source_ids": list(current.evidence_chunk_ids),
                "latency_ms": 10.0,
                "technical_error": None,
                "auditor_invoked": True,
                "auditor_approved": True,
            },
        }
        for current in items
    ]


def test_final_summary_is_deterministic_for_perfect_predictions() -> None:
    items = final_items()
    records = final_records(items)

    first = summarize_final_test(records, items, bootstrap_resamples=20, seed=9)
    second = summarize_final_test(records, items, bootstrap_resamples=20, seed=9)

    assert first == second
    assert first["item_count"] == 64
    assert first["metrics"]["macro_f1"] == 1.0
    assert first["metrics"]["abstention"]["recall"] == 1.0
    assert first["bootstrap"]["95_percentile_interval"]["macro_f1"] == {
        "lower": 1.0,
        "median": 1.0,
        "upper": 1.0,
    }


def test_final_checkpoint_rejects_development_partition() -> None:
    items = final_items()
    contaminated = (replace(items[0], split=DatasetSplit.DEVELOPMENT), *items[1:])

    with pytest.raises(EndToEndDatasetError, match="somente o teste congelado"):
        validate_final_test_checkpoint((), contaminated)


def test_final_checkpoint_rejects_wrong_prefix() -> None:
    items = final_items()
    records = final_records(items)
    records[0]["item_id"] = "outro"

    with pytest.raises(EndToEndDatasetError, match="prefixo"):
        validate_final_test_checkpoint(records, items)


def test_final_summary_requires_complete_checkpoint() -> None:
    items = final_items()

    with pytest.raises(EndToEndDatasetError, match="64 itens"):
        summarize_final_test(final_records(items)[:-1], items, bootstrap_resamples=10)
