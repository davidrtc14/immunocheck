from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from immunocheck.domain.models import (
    ContentSubmission,
    DraftVerdict,
    Evidence,
    ExtractedClaim,
    VerificationReport,
)


class ContentNormalizer(Protocol):
    def normalize(self, submission: ContentSubmission) -> str: ...


class ClaimExtractor(Protocol):
    def extract(self, normalized_text: str) -> ExtractedClaim | None: ...


class EvidenceRetriever(Protocol):
    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]: ...


class VerdictGenerator(Protocol):
    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict: ...


class FaithfulnessVerifier(Protocol):
    def verify(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> VerificationReport: ...
