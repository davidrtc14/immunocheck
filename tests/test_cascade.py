from __future__ import annotations

from immunocheck.application.cascade import SupportedVerificationCascade
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict

SUBMISSION = ContentSubmission(
    kind=ContentKind.TEXT, text="A vacina contra HPV é dada em duas doses."
)


class _Runner:
    def __init__(self, verdict: Verdict, tag: str, sink: list | None = None) -> None:
        self.verdict, self.tag, self.sink, self.calls = verdict, tag, sink, 0

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self.calls += 1
        if self.sink is not None:
            self.sink.append({"from": self.tag})
        return FactCheckResult(verdict=self.verdict, explanation=self.tag)


def _cascade(first: Verdict, second: Verdict) -> tuple[SupportedVerificationCascade, _Runner, list]:
    traces: list = []
    verifier_traces: list = []
    verifier = _Runner(second, "v5", verifier_traces)
    cascade = SupportedVerificationCascade(
        _Runner(first, "v3"), verifier, traces.append, verifier_traces=verifier_traces
    )
    return cascade, verifier, traces


def test_non_supported_from_v3_skips_the_verifier() -> None:
    for verdict in (Verdict.REFUTED, Verdict.MISLEADING, Verdict.INSUFFICIENT_EVIDENCE):
        cascade, verifier, traces = _cascade(verdict, Verdict.SUPPORTED)
        result = cascade.run(SUBMISSION)
        assert result.verdict is verdict and result.explanation == "v3" and verifier.calls == 0
        assert traces[-1] == {
            "primary_verdict": verdict.value,
            "verified": False,
            "final_verdict": verdict.value,
        }


def test_supported_confirmed_keeps_the_v3_answer() -> None:
    cascade, verifier, traces = _cascade(Verdict.SUPPORTED, Verdict.SUPPORTED)
    result = cascade.run(SUBMISSION)
    assert result.explanation == "v3" and verifier.calls == 1
    assert traces[-1]["verified"] and traces[-1]["verifier_trace"] == {"from": "v5"}


def test_supported_not_confirmed_uses_the_verifier_answer() -> None:
    for verdict in (Verdict.REFUTED, Verdict.MISLEADING, Verdict.INSUFFICIENT_EVIDENCE):
        cascade, _, traces = _cascade(Verdict.SUPPORTED, verdict)
        result = cascade.run(SUBMISSION)
        assert result.verdict is verdict and result.explanation == "v5"
        assert traces[-1]["final_verdict"] == verdict.value
