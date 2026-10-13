from __future__ import annotations

import json

import pytest

from immunocheck.application.abstention import (
    LOW_SIGNAL_EXPLANATION,
    AbstainingPipeline,
    AbstentionThresholds,
    CalibrationRecord,
    RecordingClaimExtractor,
    RecordingRetriever,
    RunSignals,
    SignalRecorder,
    abstention_curve,
    calibrate_thresholds,
)
from immunocheck.domain.models import (
    ContentKind,
    ContentSubmission,
    Evidence,
    ExtractedClaim,
    FactCheckResult,
    Verdict,
)

SUPPORTED, REFUTED, INSUFFICIENT = "SUPPORTED", "REFUTED", "INSUFFICIENT_EVIDENCE"


def ev(score: float) -> Evidence:
    return Evidence("d:p1:c1:a", "t", "s", "d", "https://x", retrieval_score=score)


def test_thresholds_trigger_on_each_signal_and_missing_values() -> None:
    signals = RunSignals(0.9, 0.5, 0.1, 3)
    assert AbstentionThresholds().reason(signals) is None
    assert AbstentionThresholds(min_confidence=0.95).reason(signals) == "confidence"
    assert AbstentionThresholds(min_top_score=0.6).reason(signals) == "top_score"
    assert AbstentionThresholds(min_margin=0.2).reason(signals) == "margin"
    assert AbstentionThresholds(min_margin=0.2).reason(RunSignals(0.9, 0.5, None, 1)) == "margin"


def test_thresholds_file_roundtrip(tmp_path) -> None:
    assert AbstentionThresholds.load(tmp_path / "nao_existe.json") == AbstentionThresholds()
    path = tmp_path / "t.json"
    body = {"thresholds": {"min_confidence": 0.8, "min_top_score": None, "min_margin": 0.02}}
    path.write_text(json.dumps(body))
    assert AbstentionThresholds.load(path) == AbstentionThresholds(0.8, None, 0.02)


class _Extractor:
    def extract(self, text):
        return ExtractedClaim("alegação", 0.7)


class _Retriever:
    def retrieve(self, claim):
        return [ev(0.80), ev(0.74), ev(0.10)]


class _Inner:
    def __init__(self, recorder, verdict) -> None:
        self.recorder, self.verdict = recorder, verdict

    def run(self, submission):
        claim = RecordingClaimExtractor(_Extractor(), self.recorder).extract("x")
        RecordingRetriever(_Retriever(), self.recorder).retrieve(claim)
        return FactCheckResult(self.verdict, "Explicação.", claim="alegação")


def _pipeline(thresholds, verdict=Verdict.SUPPORTED) -> AbstainingPipeline:
    recorder = SignalRecorder()
    return AbstainingPipeline(_Inner(recorder, verdict), recorder, thresholds)


SUB = ContentSubmission(kind=ContentKind.TEXT, text="x")


def test_pipeline_records_signals_and_abstains_only_below_threshold() -> None:
    open_result = _pipeline(AbstentionThresholds(min_margin=0.01)).run(SUB)
    assert open_result.verdict is Verdict.SUPPORTED

    pipeline = _pipeline(AbstentionThresholds(min_confidence=0.8))
    result = pipeline.run(SUB)
    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.explanation == LOW_SIGNAL_EXPLANATION and result.claim == "alegação"
    assert pipeline.last_signals.confidence == 0.7
    assert pipeline.last_signals.margin == pytest.approx(0.06)
    assert pipeline.last_signals.evidence_count == 3


def test_existing_abstention_is_untouched() -> None:
    pipeline = _pipeline(AbstentionThresholds(min_confidence=0.99), Verdict.INSUFFICIENT_EVIDENCE)
    assert pipeline.run(SUB).explanation == "Explicação."


def _records() -> list[CalibrationRecord]:
    rows = []
    for index in range(12):  # conclusões corretas com sinais fortes
        label = SUPPORTED if index % 2 else REFUTED
        rows.append(CalibrationRecord(label, label, RunSignals(0.95, 0.8, 0.10, 15)))
    for _ in range(6):  # abstenções esperadas respondidas com conclusão, sinais fracos
        rows.append(CalibrationRecord(INSUFFICIENT, SUPPORTED, RunSignals(0.5, 0.45, 0.01, 15)))
    return rows


def test_calibration_finds_threshold_that_separates_weak_signals() -> None:
    thresholds, report = calibrate_thresholds(_records(), steps=6)

    assert report["selected_macro_f1"] > report["baseline_macro_f1"]
    curve = abstention_curve(_records(), thresholds)
    assert curve["abstention_precision"] == 1.0 and curve["correct_conclusions_sacrificed"] == 0
    assert thresholds.reason(RunSignals(0.5, 0.45, 0.01, 15)) is not None
    assert thresholds.reason(RunSignals(0.95, 0.8, 0.10, 15)) is None


def test_calibration_requires_enough_records() -> None:
    with pytest.raises(ValueError):
        calibrate_thresholds(_records()[:5])
