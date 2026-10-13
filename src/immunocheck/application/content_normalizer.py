from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from immunocheck.application.text_components import TextNormalizer
from immunocheck.domain.models import ContentKind, ContentSubmission


# Link (até 50.000) e OCR (até 12.000) chegam longos; o extrator só precisa do início.
MAX_EXTRACTED_CHARS = 6_000


class ContentExtractionError(RuntimeError):
    """Falha segura e apresentável na conversão da entrada para texto."""


class ImageTextExtractor(Protocol):
    def extract(self, submission: ContentSubmission) -> str: ...


class LinkTextExtractor(Protocol):
    def extract(self, url: str) -> str: ...


@dataclass(frozen=True, slots=True)
class MultimodalNormalizer:
    image_extractor: ImageTextExtractor
    link_extractor: LinkTextExtractor
    text_normalizer: TextNormalizer = field(default_factory=TextNormalizer)
    max_extracted_chars: int = MAX_EXTRACTED_CHARS

    def normalize(self, submission: ContentSubmission) -> str:
        if submission.kind is ContentKind.TEXT:
            return self.text_normalizer.normalize(submission)
        if submission.kind is ContentKind.IMAGE:
            return self._bounded(self.image_extractor.extract(submission))
        if submission.kind is ContentKind.LINK and submission.url is not None:
            return self._bounded(self.link_extractor.extract(submission.url))
        raise ContentExtractionError("O tipo de conteúdo não pôde ser normalizado.")

    def _bounded(self, text: str) -> str:
        if len(text) <= self.max_extracted_chars:
            return text
        cut = text[: self.max_extracted_chars]
        boundary = cut.rfind(" ")
        return cut[:boundary] if boundary > self.max_extracted_chars // 2 else cut
