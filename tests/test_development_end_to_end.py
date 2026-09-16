from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.evaluation.development_end_to_end import (
    END_TO_END_CONDITIONS,
    load_checkpoint,
    summarize_end_to_end_records,
    validate_checkpoint_prefix,
)
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError
from tests.test_lexical_baseline import fixture_items


def records_for_development():
    items = tuple(item for item in fixture_items() if item.split is DatasetSplit.DEVELOPMENT)
    records = []
    for item in items:
        condition = {
            "verdict": item.label.value,
            "source_ids": list(item.evidence_chunk_ids),
            "latency_ms": 10.0,
            "technical_error": None,
            "auditor_invoked": True,
            "auditor_approved": True,
        }
        records.append(
            {
                "item_id": item.item_id,
                "claim_family": item.claim_family,
                "expected_label": item.label.value,
                "extraction": {
                    "claim": item.claim,
                    "latency_ms": 1.0,
                    "technical_error": None,
                },
                "conditions": {name: deepcopy(condition) for name in END_TO_END_CONDITIONS},
            }
        )
    return items, records


def test_summary_of_perfect_predictions_is_deterministic() -> None:
    items, records = records_for_development()

    first = summarize_end_to_end_records(records, items, bootstrap_resamples=20, seed=7)
    second = summarize_end_to_end_records(records, items, bootstrap_resamples=20, seed=7)

    assert first == second
    assert first["systems"]["dense_with_auditor"]["macro_f1"] == 1.0
    assert first["bootstrap"]["paired_macro_f1_deltas_95_percentile_interval"][
        "dense_with_auditor_minus_dense_no_auditor"
    ] == {"lower": 0.0, "median": 0.0, "upper": 0.0}


def test_checkpoint_rejects_test_items_and_wrong_prefix() -> None:
    development = fixture_items()
    all_items = (replace(development[0], split=DatasetSplit.TEST), *development[1:])
    with pytest.raises(EndToEndDatasetError, match="somente desenvolvimento"):
        validate_checkpoint_prefix((), all_items)

    items, records = records_for_development()
    records[0]["item_id"] = "outro"
    with pytest.raises(EndToEndDatasetError, match="prefixo"):
        validate_checkpoint_prefix(records, items)


def test_checkpoint_loader_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "checkpoint.jsonl"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(EndToEndDatasetError, match="inválido"):
        load_checkpoint(path)
