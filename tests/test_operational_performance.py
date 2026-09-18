from __future__ import annotations

import pytest

from immunocheck.evaluation.operational_performance import (
    summarize_latency,
    summarize_modality,
)


def test_latency_summary_uses_nearest_rank_p95() -> None:
    summary = summarize_latency(list(range(1, 31)), target_ms=29)

    assert summary["samples"] == 30
    assert summary["median_ms"] == 15.5
    assert summary["p95_ms"] == 29
    assert summary["target_met"] is True


def test_modality_summary_counts_failures_in_completion_rate() -> None:
    records = [
        {
            "total_latency_ms": float(index),
            "normalization_latency_ms": float(index) / 2,
            "technical_error": "RuntimeError" if index == 30 else None,
        }
        for index in range(1, 31)
    ]

    summary = summarize_modality(records, target_ms=45_000)

    assert summary["runs"] == 30
    assert summary["successful_runs"] == 29
    assert summary["completion_rate"] == 29 / 30
    assert summary["completion_target_met"] is True


@pytest.mark.parametrize("values", ([], [-1], [float("nan")]))
def test_latency_summary_rejects_invalid_series(values: list[float]) -> None:
    with pytest.raises(ValueError):
        summarize_latency(values, target_ms=1)
