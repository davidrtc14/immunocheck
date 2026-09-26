from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from immunocheck.application.routed_pipeline import RoutedFactCheckPipeline
from immunocheck.domain.models import (
    ContentKind,
    ContentSubmission,
    DraftVerdict,
    Evidence,
    ExtractedClaim,
    Verdict,
)


def _evidence(index: int, *, document: str = "doc") -> Evidence:
    return Evidence(
        chunk_id=f"{document}:p1:c{index}:hash{index}",
        text=f"Trecho {index}",
        source_name="Fonte oficial",
        document_title="Documento",
        url="https://example.gov.br/documento",
        page=1,
    )


CORPUS = tuple(_evidence(index) for index in range(1, 18))
CLAIM = ExtractedClaim("Alegação principal.", 0.95, True)


class Normalizer:
    def normalize(self, submission: ContentSubmission) -> str:
        return submission.text or "conteúdo normalizado"


@dataclass
class Extractor:
    claim: ExtractedClaim | None = CLAIM

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        del normalized_text
        return self.claim


@dataclass
class Retriever:
    evidence: Sequence[Evidence] = CORPUS[:15]
    calls: int = 0

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        del claim
        self.calls += 1
        return self.evidence


@dataclass
class Router:
    route: str
    explanation: str = "Estrutura identificada."

    def analyze(self, claim: ExtractedClaim) -> Router:
        del claim
        return self


@dataclass
class Generator:
    verdict: Verdict = Verdict.SUPPORTED
    source_ids: tuple[str, ...] = (CORPUS[0].chunk_id,)
    calls: list[tuple[Evidence, ...]] = field(default_factory=list)

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        del claim
        self.calls.append(tuple(evidence))
        return DraftVerdict(
            verdict=self.verdict,
            explanation="Decisão sustentada documentalmente.",
            source_ids=self.source_ids,
            correct_fact="Fato correto." if self.verdict is Verdict.REFUTED else None,
            omitted_or_distorted=(
                "A generalização omite limites." if self.verdict is Verdict.MISLEADING else None
            ),
        )


@dataclass
class Selector:
    outputs: list[tuple[str, ...]]
    calls: list[tuple[DraftVerdict, tuple[Evidence, ...]]] = field(default_factory=list)

    def select(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> tuple[str, ...]:
        del claim
        self.calls.append((draft, tuple(evidence)))
        return self.outputs.pop(0)


def _pipeline(
    route: str,
    *,
    direct: Generator | None = None,
    relation: Generator | None = None,
    selector: Selector | None = None,
    extractor: Extractor | None = None,
    retriever: Retriever | None = None,
) -> RoutedFactCheckPipeline:
    return RoutedFactCheckPipeline(
        normalizer=Normalizer(),
        claim_extractor=extractor or Extractor(),
        retriever=retriever or Retriever(),
        direct_generator=direct or Generator(),
        relation_generator=relation or Generator(),
        router=Router(route),
        citation_selector=selector
        or Selector([(CORPUS[0].chunk_id,), (CORPUS[1].chunk_id,)]),
        corpus=CORPUS,
    )


def _submission() -> ContentSubmission:
    return ContentSubmission(kind=ContentKind.TEXT, text="Conteúdo")


def test_simple_route_uses_six_chunks_and_hierarchical_sources() -> None:
    direct = Generator(verdict=Verdict.REFUTED)
    relation = Generator()
    selector = Selector([(CORPUS[5].chunk_id,), (CORPUS[6].chunk_id,)])
    pipeline = _pipeline(
        "GENERAL_SIMPLE",
        direct=direct,
        relation=relation,
        selector=selector,
    )

    result = pipeline.run(_submission())

    assert len(direct.calls[0]) == 6
    assert relation.calls == []
    assert len(selector.calls) == 2
    assert selector.calls[1][0].source_ids == (CORPUS[5].chunk_id,)
    assert CORPUS[6] in selector.calls[1][1]
    assert result.verdict is Verdict.REFUTED
    assert result.sources[0].chunk_id == CORPUS[6].chunk_id
    assert result.sources[0].source_name == "Fonte oficial"
    assert result.multiple_claims_detected is True


def test_relational_route_uses_all_fifteen_chunks() -> None:
    direct = Generator()
    relation = Generator(verdict=Verdict.MISLEADING)
    pipeline = _pipeline("PREMISE_CONCLUSION", direct=direct, relation=relation)

    result = pipeline.run(_submission())

    assert direct.calls == []
    assert len(relation.calls[0]) == 15
    assert result.verdict is Verdict.MISLEADING
    assert result.omitted_or_distorted == "A generalização omite limites."


def test_unanchored_event_abstains_without_generating_or_selecting() -> None:
    direct = Generator()
    relation = Generator()
    selector = Selector([])
    pipeline = _pipeline(
        "UNANCHORED_SPECIFIC_EVENT",
        direct=direct,
        relation=relation,
        selector=selector,
    )

    result = pipeline.run(_submission())

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.explanation == "Estrutura identificada."
    assert direct.calls == relation.calls == selector.calls == []


def test_invalid_generator_or_selector_source_fails_closed() -> None:
    invalid_generator = Generator(source_ids=("inventado",))
    result = _pipeline("GENERAL_SIMPLE", direct=invalid_generator).run(_submission())
    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources == ()

    invalid_selector = Selector([("inventado",)])
    result = _pipeline("GENERAL_SIMPLE", selector=invalid_selector).run(_submission())
    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources == ()


def test_generator_abstention_preserves_only_valid_partial_sources() -> None:
    direct = Generator(verdict=Verdict.INSUFFICIENT_EVIDENCE)
    selector = Selector([])

    result = _pipeline("GENERAL_SIMPLE", direct=direct, selector=selector).run(_submission())

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.sources[0].chunk_id == CORPUS[0].chunk_id
    assert selector.calls == []


def test_missing_claim_and_empty_retrieval_abstain_early() -> None:
    retriever = Retriever()
    no_claim = _pipeline("GENERAL_SIMPLE", extractor=Extractor(None), retriever=retriever)
    assert no_claim.run(_submission()).verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert retriever.calls == 0

    empty = _pipeline("GENERAL_SIMPLE", retriever=Retriever(()))
    assert empty.run(_submission()).verdict is Verdict.INSUFFICIENT_EVIDENCE


def test_unknown_route_fails_closed() -> None:
    result = _pipeline("UNKNOWN").run(_submission())

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert "forma da alegação" in result.explanation
