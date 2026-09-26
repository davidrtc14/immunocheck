from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from immunocheck.application.ports import (
    ClaimExtractor,
    ContentNormalizer,
    EvidenceRetriever,
    VerdictGenerator,
)
from immunocheck.domain.input_policy import InputLimits, validate_submission
from immunocheck.domain.models import (
    ContentSubmission,
    DraftVerdict,
    Evidence,
    ExtractedClaim,
    FactCheckResult,
    SourceReference,
    Verdict,
)
from immunocheck.retrieval.document_expansion import expand_document_candidates

GENERAL_SIMPLE = "GENERAL_SIMPLE"
PREMISE_CONCLUSION = "PREMISE_CONCLUSION"
UNANCHORED_SPECIFIC_EVENT = "UNANCHORED_SPECIFIC_EVENT"


class ClaimRoute(Protocol):
    route: str
    explanation: str


class ClaimRouter(Protocol):
    def analyze(self, claim: ExtractedClaim) -> ClaimRoute: ...


class CitationSelector(Protocol):
    def select(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> tuple[str, ...]: ...


@dataclass(slots=True)
class RoutedFactCheckPipeline:
    """Pipeline v3 confirmada: roteamento estrutural e citações hierárquicas."""

    normalizer: ContentNormalizer
    claim_extractor: ClaimExtractor
    retriever: EvidenceRetriever
    direct_generator: VerdictGenerator
    relation_generator: VerdictGenerator
    router: ClaimRouter
    citation_selector: CitationSelector
    corpus: Sequence[Evidence]
    direct_top_k: int = 6
    input_limits: InputLimits = field(default_factory=InputLimits)

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        validate_submission(submission, self.input_limits)
        normalized_text = self.normalizer.normalize(submission)
        claim = self.claim_extractor.extract(normalized_text)
        if claim is None:
            return FactCheckResult.insufficient(
                "Não foi possível identificar uma alegação factual verificável."
            )

        evidence = tuple(self.retriever.retrieve(claim))
        if not evidence:
            return self._insufficient(
                claim,
                "As fontes disponíveis não fornecem evidência suficiente para concluir.",
            )

        route = self.router.analyze(claim)
        if route.route == UNANCHORED_SPECIFIC_EVENT:
            return self._insufficient(claim, route.explanation)
        if route.route == GENERAL_SIMPLE:
            draft = self.direct_generator.generate(claim, evidence[: self.direct_top_k])
            decision_evidence = evidence[: self.direct_top_k]
        elif route.route == PREMISE_CONCLUSION:
            draft = self.relation_generator.generate(claim, evidence)
            decision_evidence = evidence
        else:
            return self._insufficient(
                claim,
                "Não foi possível determinar com segurança a forma da alegação.",
            )

        decision_by_id = {item.chunk_id: item for item in decision_evidence}
        draft_source_ids = tuple(dict.fromkeys(draft.source_ids))
        if any(source_id not in decision_by_id for source_id in draft_source_ids):
            return self._insufficient(
                claim,
                "A resposta gerada não apresentou fontes válidas e verificáveis.",
            )

        if draft.verdict is Verdict.INSUFFICIENT_EVIDENCE:
            partial_sources = tuple(
                SourceReference.from_evidence(decision_by_id[source_id])
                for source_id in draft_source_ids
            )
            return self._insufficient(
                claim,
                draft.explanation,
                sources=partial_sources,
            )
        if not draft_source_ids:
            return self._insufficient(
                claim,
                "A resposta gerada não apresentou fontes válidas e verificáveis.",
            )

        seeds = self._valid_selection(
            self.citation_selector.select(claim, draft, evidence),
            evidence,
        )
        if not seeds:
            return self._insufficient(
                claim,
                "A seleção de fontes não apresentou referências válidas e verificáveis.",
            )

        expanded = expand_document_candidates(
            self.corpus,
            seeds,
            first_chunks=4,
            neighbor_radius=1,
            max_candidates=20,
        )
        selection_draft = DraftVerdict(
            verdict=draft.verdict,
            explanation=draft.explanation,
            source_ids=seeds,
            correct_fact=draft.correct_fact,
            omitted_or_distorted=draft.omitted_or_distorted,
        )
        final_ids = self._valid_selection(
            self.citation_selector.select(claim, selection_draft, expanded),
            expanded,
        )
        if not final_ids:
            return self._insufficient(
                claim,
                "A seleção de fontes não apresentou referências válidas e verificáveis.",
            )

        expanded_by_id = {item.chunk_id: item for item in expanded}
        sources = tuple(
            SourceReference.from_evidence(expanded_by_id[source_id])
            for source_id in final_ids
        )
        return FactCheckResult(
            verdict=draft.verdict,
            explanation=draft.explanation,
            claim=claim.text,
            correct_fact=draft.correct_fact,
            omitted_or_distorted=draft.omitted_or_distorted,
            sources=sources,
            multiple_claims_detected=claim.multiple_claims_detected,
        )

    @staticmethod
    def _valid_selection(
        source_ids: Sequence[str],
        evidence: Sequence[Evidence],
    ) -> tuple[str, ...]:
        normalized = tuple(dict.fromkeys(source_ids))
        available = {item.chunk_id for item in evidence}
        if any(source_id not in available for source_id in normalized):
            return ()
        return normalized

    @staticmethod
    def _insufficient(
        claim: ExtractedClaim,
        explanation: str,
        *,
        sources: tuple[SourceReference, ...] = (),
    ) -> FactCheckResult:
        return FactCheckResult.insufficient(
            explanation,
            claim=claim.text,
            sources=sources,
            multiple_claims_detected=claim.multiple_claims_detected,
        )
