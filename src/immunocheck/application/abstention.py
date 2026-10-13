"""D2: abstenção calibrada por sinais numéricos (confiança da extração, score e margem)."""

from __future__ import annotations

import itertools
import json
import threading
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol

from sklearn.metrics import f1_score

from immunocheck.application.ports import ClaimExtractor, EvidenceRetriever
from immunocheck.domain.models import (
    ContentSubmission,
    Evidence,
    ExtractedClaim,
    FactCheckResult,
    Verdict,
)

LOW_SIGNAL_EXPLANATION = (
    "Os sinais de confiança da análise (extração da alegação e proximidade das fontes) ficaram "
    "abaixo do mínimo calibrado, então o sistema se abstém de concluir."
)
LABELS = [verdict.value for verdict in Verdict]


@dataclass(frozen=True, slots=True)
class RunSignals:
    confidence: float | None
    top_score: float | None
    margin: float | None
    evidence_count: int


@dataclass(frozen=True, slots=True)
class AbstentionThresholds:
    """Limiares mínimos; `None` desativa o sinal. Congelados em arquivo após a calibração."""

    min_confidence: float | None = None
    min_top_score: float | None = None
    min_margin: float | None = None

    def reason(self, signals: RunSignals) -> str | None:
        checks = (
            ("confidence", signals.confidence, self.min_confidence),
            ("top_score", signals.top_score, self.min_top_score),
            ("margin", signals.margin, self.min_margin),
        )
        for name, value, minimum in checks:
            if minimum is not None and (value is None or value < minimum):
                return name
        return None

    @classmethod
    def load(cls, path: Path) -> AbstentionThresholds:
        if not path.is_file():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**{key: data["thresholds"].get(key) for key in asdict(cls())})


class SignalRecorder:
    """Guarda os sinais da execução corrente por thread; nunca persiste conteúdo."""

    def __init__(self) -> None:
        self._state = threading.local()

    def reset(self) -> None:
        self._state.claim = None
        self._state.evidence = ()

    def signals(self) -> RunSignals:
        claim: ExtractedClaim | None = getattr(self._state, "claim", None)
        evidence: Sequence[Evidence] = getattr(self._state, "evidence", ())
        scores = [item.retrieval_score for item in evidence if item.retrieval_score is not None]
        top = scores[0] if scores else None
        margin = scores[0] - scores[1] if len(scores) > 1 else None
        return RunSignals(
            confidence=claim.confidence if claim else None,
            top_score=top,
            margin=margin,
            evidence_count=len(evidence),
        )


class RecordingClaimExtractor:
    def __init__(self, delegate: ClaimExtractor, recorder: SignalRecorder) -> None:
        self._delegate, self._recorder = delegate, recorder

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        claim = self._delegate.extract(normalized_text)
        self._recorder._state.claim = claim
        return claim


class RecordingRetriever:
    def __init__(self, delegate: EvidenceRetriever, recorder: SignalRecorder) -> None:
        self._delegate, self._recorder = delegate, recorder

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        evidence = tuple(self._delegate.retrieve(claim))
        self._recorder._state.evidence = evidence
        return evidence


class Runner(Protocol):
    def run(self, submission: ContentSubmission) -> FactCheckResult: ...


@dataclass(slots=True)
class AbstainingPipeline:
    inner: Runner
    recorder: SignalRecorder
    thresholds: AbstentionThresholds = field(default_factory=AbstentionThresholds)
    last_signals: RunSignals | None = None
    last_inner_result: FactCheckResult | None = None

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self.recorder.reset()
        result = self.inner.run(submission)
        signals = self.recorder.signals()
        self.last_signals, self.last_inner_result = signals, result
        if result.verdict is Verdict.INSUFFICIENT_EVIDENCE:
            return result
        if self.thresholds.reason(signals) is None:
            return result
        return FactCheckResult.insufficient(
            LOW_SIGNAL_EXPLANATION,
            claim=result.claim,
            sources=result.sources,
            multiple_claims_detected=result.multiple_claims_detected,
        )


# --- calibração offline -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CalibrationRecord:
    expected: str
    predicted: str
    signals: RunSignals


def _apply(record: CalibrationRecord, thresholds: AbstentionThresholds) -> str:
    if record.predicted == Verdict.INSUFFICIENT_EVIDENCE.value:
        return record.predicted
    if thresholds.reason(record.signals) is None:
        return record.predicted
    return Verdict.INSUFFICIENT_EVIDENCE.value


def macro_f1_with(records: Sequence[CalibrationRecord], thresholds: AbstentionThresholds) -> float:
    expected = [record.expected for record in records]
    predicted = [_apply(record, thresholds) for record in records]
    return float(f1_score(expected, predicted, labels=LABELS, average="macro", zero_division=0))


def abstention_curve(
    records: Sequence[CalibrationRecord],
    thresholds: AbstentionThresholds,
) -> dict[str, float | int]:
    """Precisão/recall da abstenção, e quantas conclusões corretas foram sacrificadas."""
    insufficient = Verdict.INSUFFICIENT_EVIDENCE.value
    final = [_apply(record, thresholds) for record in records]
    abstained = [i for i, label in enumerate(final) if label == insufficient]
    true_abstentions = [i for i in abstained if records[i].expected == insufficient]
    should_abstain = sum(record.expected == insufficient for record in records)
    sacrificed = sum(
        1
        for i in abstained
        if records[i].expected != insufficient and records[i].predicted == records[i].expected
    )
    return {
        "abstentions": len(abstained),
        "abstention_precision": len(true_abstentions) / len(abstained) if abstained else 0.0,
        "abstention_recall": len(true_abstentions) / should_abstain if should_abstain else 0.0,
        "correct_conclusions_sacrificed": sacrificed,
    }


def _candidate_values(values: Sequence[float | None], steps: int) -> list[float | None]:
    present = sorted({round(v, 6) for v in values if v is not None})
    if not present:
        return [None]
    picks = {present[min(len(present) - 1, int(i * len(present) / steps))] for i in range(1, steps)}
    return [None, *sorted(picks)]


def calibrate_thresholds(
    records: Sequence[CalibrationRecord],
    *,
    steps: int = 6,
    max_sacrificed_fraction: float = 0.25,
) -> tuple[AbstentionThresholds, dict[str, object]]:
    """Escolhe o limiar de maior macro-F1, com desempate por menos sinais ativos e menos abstenção.

    Restrição: não sacrificar mais que `max_sacrificed_fraction` das conclusões corretas, para
    evitar uma política que "acerta" abstendo-se de quase tudo.
    """
    if len(records) < 12:
        raise ValueError("A calibração exige ao menos 12 registros.")
    correct_conclusions = sum(
        r.predicted == r.expected and r.expected != Verdict.INSUFFICIENT_EVIDENCE.value
        for r in records
    )
    grids = [
        _candidate_values([r.signals.confidence for r in records], steps),
        _candidate_values([r.signals.top_score for r in records], steps),
        _candidate_values([r.signals.margin for r in records], steps),
    ]
    baseline = AbstentionThresholds()
    best, best_key = baseline, None
    table: list[dict[str, object]] = []
    for confidence, top, margin in itertools.product(*grids):
        candidate = AbstentionThresholds(confidence, top, margin)
        curve = abstention_curve(records, candidate)
        if correct_conclusions and (
            curve["correct_conclusions_sacrificed"] > max_sacrificed_fraction * correct_conclusions
        ):
            continue
        score = macro_f1_with(records, candidate)
        active = sum(v is not None for v in (confidence, top, margin))
        key = (round(score, 6), -active, -int(curve["abstentions"]))
        table.append({"thresholds": asdict(candidate), "macro_f1": score, **curve})
        if best_key is None or key > best_key:
            best, best_key = candidate, key
    return best, {
        "records": len(records),
        "baseline_macro_f1": macro_f1_with(records, baseline),
        "selected_macro_f1": macro_f1_with(records, best),
        "selected_curve": abstention_curve(records, best),
        "candidates_evaluated": len(table),
        "max_sacrificed_fraction": max_sacrificed_fraction,
    }


def records_from_checkpoint(rows: Sequence[Mapping[str, object]]) -> list[CalibrationRecord]:
    """Reconstrói registros de calibração a partir do checkpoint do experimento."""
    out: list[CalibrationRecord] = []
    for row in rows:
        sig = row["signals"]
        out.append(
            CalibrationRecord(
                expected=str(row["expected_label"]),
                predicted=str(row["verdict"]),
                signals=RunSignals(**sig),  # type: ignore[arg-type]
            )
        )
    return out
