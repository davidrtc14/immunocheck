from __future__ import annotations

from dataclasses import dataclass, field

from immunocheck.application.ports import (
    ClaimExtractor,
    ContentNormalizer,
    EvidenceRetriever,
    EvidenceSufficiencyAssessor,
    FaithfulnessVerifier,
    VerdictGenerator,
)
from immunocheck.domain.input_policy import InputLimits, validate_submission
from immunocheck.domain.models import ContentSubmission, FactCheckResult, SourceReference, Verdict


@dataclass(slots=True)
class FactCheckPipeline:
    normalizer: ContentNormalizer
    claim_extractor: ClaimExtractor
    retriever: EvidenceRetriever
    generator: VerdictGenerator
    verifier: FaithfulnessVerifier
    sufficiency_assessor: EvidenceSufficiencyAssessor | None = None
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
                multiple_claims_detected=claim.multiple_claims_detected,
            )

        evidence_by_id = {item.chunk_id: item for item in evidence}
        if self.sufficiency_assessor is not None:
            assessment = self.sufficiency_assessor.assess(claim, evidence)
            assessed_source_ids = tuple(dict.fromkeys(assessment.source_ids))
            if any(source_id not in evidence_by_id for source_id in assessed_source_ids):
                return FactCheckResult.insufficient(
                    "A avaliação de suficiência não apresentou fontes válidas e verificáveis.",
                    claim=claim.text,
                    multiple_claims_detected=claim.multiple_claims_detected,
                )
            assessed_evidence = tuple(
                evidence_by_id[source_id] for source_id in assessed_source_ids
            )
            assessed_sources = tuple(
                SourceReference.from_evidence(item) for item in assessed_evidence
            )
            if not assessment.sufficient:
                return FactCheckResult.insufficient(
                    assessment.explanation,
                    claim=claim.text,
                    sources=assessed_sources,
                    multiple_claims_detected=claim.multiple_claims_detected,
                )
            if not assessed_evidence:
                return FactCheckResult.insufficient(
                    "As fontes disponíveis não fornecem evidência suficiente para concluir.",
                    claim=claim.text,
                    multiple_claims_detected=claim.multiple_claims_detected,
                )
            evidence = assessed_evidence
            evidence_by_id = {item.chunk_id: item for item in evidence}

        draft = self.generator.generate(claim, evidence)
        cited_source_ids = tuple(dict.fromkeys(draft.source_ids))
        if any(source_id not in evidence_by_id for source_id in cited_source_ids):
            return FactCheckResult.insufficient(
                "A resposta gerada não apresentou fontes válidas e verificáveis.",
                claim=claim.text,
                multiple_claims_detected=claim.multiple_claims_detected,
            )

        cited_evidence = tuple(evidence_by_id[source_id] for source_id in cited_source_ids)
        sources = tuple(SourceReference.from_evidence(item) for item in cited_evidence)
        if draft.verdict is Verdict.INSUFFICIENT_EVIDENCE:
            if not cited_evidence:
                return FactCheckResult.insufficient(
                    draft.explanation,
                    claim=claim.text,
                    multiple_claims_detected=claim.multiple_claims_detected,
                )
            verification = self.verifier.verify(claim, draft, cited_evidence)
            explanation = (
                draft.explanation
                if verification.all_supported
                else "As fontes recuperadas não permitem avaliar com segurança todas as partes da alegação."
            )
            return FactCheckResult.insufficient(
                explanation,
                claim=claim.text,
                sources=sources,
                multiple_claims_detected=claim.multiple_claims_detected,
            )

        if not cited_evidence:
            return FactCheckResult.insufficient(
                "A resposta gerada não apresentou fontes válidas e verificáveis.",
                claim=claim.text,
                multiple_claims_detected=claim.multiple_claims_detected,
            )

        verification = self.verifier.verify(claim, draft, cited_evidence)
        if not verification.all_supported:
            return FactCheckResult.insufficient(
                "As fontes recuperadas não permitem avaliar com segurança todas as partes da alegação.",
                claim=claim.text,
                sources=sources,
                multiple_claims_detected=claim.multiple_claims_detected,
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
