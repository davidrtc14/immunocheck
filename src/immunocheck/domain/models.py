from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ContentKind(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    LINK = "link"


class Verdict(StrEnum):
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    MISLEADING = "MISLEADING"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True, slots=True)
class ContentSubmission:
    kind: ContentKind
    text: str | None = None
    url: str | None = None
    data: bytes | None = None
    media_type: str | None = None
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True, slots=True)
class ExtractedClaim:
    text: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("A alegação extraída não pode ser vazia.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("A confiança da extração deve estar entre 0 e 1.")


@dataclass(frozen=True, slots=True)
class Evidence:
    chunk_id: str
    text: str
    source_name: str
    document_title: str
    url: str
    publication_date: str | None = None
    page: int | None = None
    retrieval_score: float | None = None


@dataclass(frozen=True, slots=True)
class DraftVerdict:
    verdict: Verdict
    explanation: str
    source_ids: tuple[str, ...]
    correct_fact: str | None = None
    omitted_or_distorted: str | None = None


@dataclass(frozen=True, slots=True)
class VerificationReport:
    all_supported: bool
    unsupported_sentences: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SourceReference:
    chunk_id: str
    source_name: str
    document_title: str
    url: str
    publication_date: str | None = None
    page: int | None = None

    @classmethod
    def from_evidence(cls, evidence: Evidence) -> SourceReference:
        return cls(
            chunk_id=evidence.chunk_id,
            source_name=evidence.source_name,
            document_title=evidence.document_title,
            url=evidence.url,
            publication_date=evidence.publication_date,
            page=evidence.page,
        )


@dataclass(frozen=True, slots=True)
class FactCheckResult:
    verdict: Verdict
    explanation: str
    claim: str | None = None
    correct_fact: str | None = None
    omitted_or_distorted: str | None = None
    sources: tuple[SourceReference, ...] = field(default_factory=tuple)

    @classmethod
    def insufficient(cls, explanation: str, claim: str | None = None) -> FactCheckResult:
        return cls(
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            explanation=explanation,
            claim=claim,
        )
