from __future__ import annotations

from dataclasses import dataclass, field

from immunocheck.application.ports import (
    ClaimExtractor,
    ContentNormalizer,
    EvidenceRetriever,
    FaithfulnessVerifier,
    VerdictGenerator,
)
from immunocheck.domain.input_policy import InputLimits, validate_submission
from immunocheck.domain.models import ContentSubmission, FactCheckResult, SourceReference


@dataclass(slots=True)
class FactCheckPipeline:
    normalizer: ContentNormalizer
    claim_extractor: ClaimExtractor
    retriever: EvidenceRetriever
    generator: VerdictGenerator
    verifier: FaithfulnessVerifier
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
            return FactCheckResult.insufficient(
                "As fontes disponíveis não fornecem evidência suficiente para concluir.",
                claim=claim.text,
            )

        draft = self.generator.generate(claim, evidence)
        evidence_by_id = {item.chunk_id: item for item in evidence}
        if not draft.source_ids or any(
            source_id not in evidence_by_id for source_id in draft.source_ids
        ):
            return FactCheckResult.insufficient(
                "A resposta gerada não apresentou fontes válidas e verificáveis.",
                claim=claim.text,
            )

        verification = self.verifier.verify(draft, evidence)
        if not verification.all_supported:
            return FactCheckResult.insufficient(
                "A explicação gerada não foi integralmente sustentada pelas fontes.",
                claim=claim.text,
            )

        sources = tuple(
            SourceReference.from_evidence(evidence_by_id[source_id])
            for source_id in dict.fromkeys(draft.source_ids)
        )
        return FactCheckResult(
            verdict=draft.verdict,
            explanation=draft.explanation,
            claim=claim.text,
            correct_fact=draft.correct_fact,
            omitted_or_distorted=draft.omitted_or_distorted,
            sources=sources,
        )
