from __future__ import annotations

import pytest

from immunocheck.domain.models import VerificationReport
from immunocheck.evaluation.auditor_calibration import apply_audit_result, draft_from_condition
from immunocheck.evaluation.end_to_end import EndToEndDatasetError


def condition(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "verdict": "MISLEADING",
        "explanation": "A afirmação mistura um fato correto com uma conclusão indevida.",
        "source_ids": ["chunk-1"],
        "correct_fact": None,
        "omitted_or_distorted": "A conclusão amplia indevidamente o alcance do fato.",
        "latency_ms": 7000.0,
        "technical_error": None,
        "auditor_invoked": False,
        "auditor_approved": None,
    }
    value.update(overrides)
    return value


def test_rebuilds_draft_from_frozen_dense_condition() -> None:
    draft = draft_from_condition(condition())

    assert draft.verdict.value == "MISLEADING"
    assert draft.source_ids == ("chunk-1",)
    assert draft.omitted_or_distorted is not None


def test_rejected_factual_audit_abstains_and_preserves_partial_sources() -> None:
    report = VerificationReport(False, ("A conclusão amplia indevidamente o alcance do fato.",))

    result = apply_audit_result(condition(), report=report, audit_latency_ms=1250.0)

    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert result["source_ids"] == ["chunk-1"]
    assert result["latency_ms"] == 8250.0
    assert result["auditor_unsupported_sentences"] == list(report.unsupported_sentences)


def test_approved_factual_audit_preserves_draft() -> None:
    result = apply_audit_result(
        condition(),
        report=VerificationReport(True),
        audit_latency_ms=500.0,
    )

    assert result["verdict"] == "MISLEADING"
    assert result["omitted_or_distorted"] is not None
    assert result["auditor_approved"] is True


def test_technical_failure_abstains_without_sources() -> None:
    result = apply_audit_result(
        condition(),
        report=None,
        audit_latency_ms=50.0,
        technical_error="OllamaError: indisponível",
    )

    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert result["source_ids"] == []
    assert result["technical_error"] == "OllamaError: indisponível"


def test_rejects_invalid_frozen_condition() -> None:
    with pytest.raises(EndToEndDatasetError, match="Citações inválidas"):
        draft_from_condition(condition(source_ids="chunk-1"))
