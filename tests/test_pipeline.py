from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.domain.models import (
    ContentKind,
    ContentSubmission,
    DraftVerdict,
    Evidence,
    ExtractedClaim,
    Verdict,
    VerificationReport,
)

EVIDENCE = Evidence(
    chunk_id="chunk-1",
    text="A fonte oficial sustenta o fato analisado.",
    source_name="Ministério da Saúde",
    document_title="Manual de vacinação",
    url="https://example.gov.br/manual",
    page=10,
)

DEFAULT_CLAIM = ExtractedClaim("A vacina é eficaz.", 0.9)


class TextNormalizer:
    def normalize(self, submission: ContentSubmission) -> str:
        assert submission.text is not None
        return submission.text.strip()


@dataclass
class StubClaimExtractor:
    claim: ExtractedClaim | None

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        return self.claim


@dataclass
class StubRetriever:
    evidence: Sequence[Evidence]
    calls: int = 0

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        self.calls += 1
        return self.evidence


@dataclass
class StubGenerator:
    draft: DraftVerdict

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        return self.draft


@dataclass
class StubVerifier:
    report: VerificationReport
    drafts: list[DraftVerdict] = field(default_factory=list)
    evidence_batches: list[tuple[Evidence, ...]] = field(default_factory=list)

    def verify(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> VerificationReport:
        del claim
        self.drafts.append(draft)
        self.evidence_batches.append(tuple(evidence))
        return self.report


def build_pipeline(
    *,
    claim: ExtractedClaim | None = DEFAULT_CLAIM,
    evidence: Sequence[Evidence] = (EVIDENCE,),
    source_ids: tuple[str, ...] = ("chunk-1",),
    supported: bool = True,
    verdict: Verdict = Verdict.SUPPORTED,
) -> tuple[FactCheckPipeline, StubRetriever]:
    retriever = StubRetriever(evidence)
    pipeline = FactCheckPipeline(
        normalizer=TextNormalizer(),
        claim_extractor=StubClaimExtractor(claim),
        retriever=retriever,
        generator=StubGenerator(
            DraftVerdict(
                verdict=verdict,
                explanation="A alegação é sustentada pela fonte oficial.",
                source_ids=source_ids,
            )
        ),
        verifier=StubVerifier(VerificationReport(all_supported=supported)),
    )
    return pipeline, retriever


def test_returns_grounded_result_with_programmatic_source() -> None:
    pipeline, _ = build_pipeline()

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.SUPPORTED
    assert result.claim == "A vacina é eficaz."
    assert result.sources[0].source_name == "Ministério da Saúde"
    assert result.sources[0].chunk_id == "chunk-1"


def test_verifier_receives_only_evidence_cited_by_generator() -> None:
    other = Evidence(
        chunk_id="chunk-2",
        text="Outro trecho recuperado.",
        source_name="Anvisa",
        document_title="Outro documento",
        url="https://example.gov.br/outro",
    )
    pipeline, _ = build_pipeline(evidence=(EVIDENCE, other))
    verifier = pipeline.verifier
    assert isinstance(verifier, StubVerifier)

    pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert verifier.evidence_batches == [(EVIDENCE,)]


def test_abstains_before_retrieval_when_claim_is_missing() -> None:
    pipeline, retriever = build_pipeline(claim=None)

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="Olá"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert retriever.calls == 0


def test_abstains_when_retrieval_returns_no_evidence() -> None:
    pipeline, _ = build_pipeline(evidence=())

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources == ()


def test_respects_insufficient_verdict_from_generator() -> None:
    pipeline, _ = build_pipeline(verdict=Verdict.INSUFFICIENT_EVIDENCE, source_ids=())

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources == ()


def test_insufficient_verdict_preserves_valid_partial_sources() -> None:
    pipeline, _ = build_pipeline(
        verdict=Verdict.INSUFFICIENT_EVIDENCE,
        source_ids=("chunk-1",),
    )

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources[0].chunk_id == "chunk-1"


def test_abstains_when_generator_references_unknown_source() -> None:
    pipeline, _ = build_pipeline(source_ids=("invented-chunk",))

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert "fontes válidas" in result.explanation


def test_abstains_when_faithfulness_check_fails() -> None:
    pipeline, _ = build_pipeline(supported=False)

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="É verdade?"))

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert "todas as partes" in result.explanation
    assert result.sources[0].chunk_id == "chunk-1"


def test_propagates_multiple_claims_notice_to_result() -> None:
    pipeline, _ = build_pipeline(claim=ExtractedClaim("A vacina é eficaz.", 0.9, True))

    result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text="Várias alegações"))

    assert result.multiple_claims_detected is True
