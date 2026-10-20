from __future__ import annotations

from typing import Any

from immunocheck.application.decomposed_pipeline import TECHNICAL_ABSTENTION
from immunocheck.application.structured_claim import (
    ClaimKind,
    Proposition,
    PropositionRole,
    PropositionType,
    StructuredClaim,
)
from immunocheck.application.text_components import ModelOutputError
from immunocheck.application.v7_fallback import DecompositionFallbackPipeline
from immunocheck.application.v7_verdict import V7FactCheckPipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict

SUBMISSION = ContentSubmission(kind=ContentKind.TEXT, text="A vacina causa autismo.")


class _Normalizer:
    def normalize(self, submission: ContentSubmission) -> str:
        return submission.text or ""


class _FailingExtractor:
    def __init__(self) -> None:
        self.calls = 0

    def extract(self, text: str, *, retry: bool = False) -> StructuredClaim | None:
        self.calls += 1
        raise ModelOutputError("saída inválida")


class _IndividualExtractor:
    def extract(self, text: str, *, retry: bool = False) -> StructuredClaim | None:
        core = Proposition(text, PropositionRole.CORE, PropositionType.FACT)
        return StructuredClaim(text, ClaimKind.INDIVIDUAL_EVENT, (core,))


class _Unused:
    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"não deveria ser chamado: {name}")


class _Fallback:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self.calls += 1
        return FactCheckResult(verdict=Verdict.REFUTED, explanation="v3")


def _pipeline(extractor: Any) -> V7FactCheckPipeline:
    return V7FactCheckPipeline(
        normalizer=_Normalizer(),
        extractor=extractor,
        retriever=_Unused(),
        judge=_Unused(),
        explainer=_Unused(),
    )


def _wrap(extractor: Any) -> tuple[DecompositionFallbackPipeline, _Fallback, list, list]:
    fallback, built, traces = _Fallback(), [], []

    def factory() -> _Fallback:
        built.append(True)
        return fallback

    wrapper = DecompositionFallbackPipeline(_pipeline(extractor), factory, trace_sink=traces.append)
    return wrapper, fallback, built, traces


def test_failed_decomposition_falls_back_to_v3() -> None:
    extractor = _FailingExtractor()
    wrapper, fallback, built, traces = _wrap(extractor)
    result = wrapper.run(SUBMISSION)
    assert extractor.calls == 2 and fallback.calls == 1 and built == [True]
    assert result.verdict is Verdict.REFUTED and result.explanation == "v3"
    assert traces == [{"technical_abstention": False, "decomposition_fallback": "v3"}]


def test_fallback_is_built_once() -> None:
    wrapper, fallback, built, _ = _wrap(_FailingExtractor())
    wrapper.run(SUBMISSION)
    wrapper.run(SUBMISSION)
    assert built == [True] and fallback.calls == 2


def test_successful_decomposition_keeps_the_v7_result() -> None:
    wrapper, fallback, built, traces = _wrap(_IndividualExtractor())
    result = wrapper.run(SUBMISSION)
    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE and result.explanation != "v3"
    assert not built and fallback.calls == 0
    assert traces[0]["claim_kind"] == ClaimKind.INDIVIDUAL_EVENT.value
    assert "decomposition_fallback" not in traces[0]


def test_technical_abstention_after_decomposition_is_kept() -> None:
    class _FailingJudge:
        def judge(self, propositions: Any, evidence: Any, *, retry: bool = False) -> Any:
            raise ModelOutputError("juiz inválido")

    class _Retriever:
        def retrieve_queries(self, queries: Any) -> list:
            return []

    class _FactExtractor:
        def extract(self, text: str, *, retry: bool = False) -> StructuredClaim:
            core = Proposition(text, PropositionRole.CORE, PropositionType.FACT)
            return StructuredClaim(text, ClaimKind.GENERAL, (core,))

    pipeline = V7FactCheckPipeline(
        normalizer=_Normalizer(),
        extractor=_FactExtractor(),
        retriever=_Retriever(),
        judge=_FailingJudge(),
        explainer=_Unused(),
    )
    built: list = []
    traces: list = []
    wrapper = DecompositionFallbackPipeline(
        pipeline, lambda: built.append(True), trace_sink=traces.append
    )
    result = wrapper.run(SUBMISSION)
    assert result.explanation == TECHNICAL_ABSTENTION and not built
    assert traces[0]["technical_abstention"] is True
