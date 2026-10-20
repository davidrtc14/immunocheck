from __future__ import annotations

import pytest

from immunocheck.evaluation.verdict_v7 import (
    grave_error,
    macro_f1,
    p95_seconds,
    paired_family_bootstrap,
    recall_by_label,
    summarize,
)


def _row(case: str, expected: str, verdict: str, family: str = "f", **extra: object) -> dict:
    return {
        "case_id": case,
        "expected_label": expected,
        "verdict": verdict,
        "claim_family": family,
        "latency_ms": 1000.0,
        "failure": None,
    } | extra


PERFECT = [
    _row("a", "SUPPORTED", "SUPPORTED", "f1"),
    _row("b", "REFUTED", "REFUTED", "f2"),
    _row("c", "MISLEADING", "MISLEADING", "f3"),
    _row("d", "INSUFFICIENT_EVIDENCE", "INSUFFICIENT_EVIDENCE", "f4"),
]


def test_macro_f1_and_recall() -> None:
    assert macro_f1(PERFECT) == 1.0
    always_insufficient = [r | {"verdict": "INSUFFICIENT_EVIDENCE"} for r in PERFECT]
    # Só a classe INSUFFICIENT acerta: precisão 1/4, recall 1, F1 0,4; média 0,1.
    assert macro_f1(always_insufficient) == pytest.approx(0.1)
    assert recall_by_label(always_insufficient)["SUPPORTED"] == 0.0


def test_grave_error_counts_only_non_supported_items() -> None:
    rows = [
        _row("a", "SUPPORTED", "SUPPORTED"),
        _row("b", "REFUTED", "SUPPORTED"),
        _row("c", "MISLEADING", "MISLEADING"),
        _row("d", "INSUFFICIENT_EVIDENCE", "SUPPORTED"),
    ]
    assert grave_error(rows) == pytest.approx(2 / 3)


def test_p95_nearest_rank_and_summary() -> None:
    rows = [_row(str(i), "SUPPORTED", "SUPPORTED", latency_ms=i * 1000.0) for i in range(1, 21)]
    assert p95_seconds(rows) == 19.0
    summary = summarize(rows[:1] + [_row("x", "REFUTED", "REFUTED", failure="ValueError")])
    assert summary["failure_rate"] == 0.5


def test_paired_family_bootstrap() -> None:
    worse = [r | {"verdict": "INSUFFICIENT_EVIDENCE"} for r in PERFECT]
    result = paired_family_bootstrap(PERFECT, worse, samples=200)
    assert result["delta"] == pytest.approx(0.9)
    assert result["ci_low"] <= result["delta"] <= result["ci_high"]
    with pytest.raises(ValueError):
        paired_family_bootstrap(PERFECT[:2], worse)
