"""Camada de compreensão da entrada multimodal (ADR-050, extração v2).

Fica entre a submissão e o extrator de alegação e entrega a ele só o texto que pode conter a
alegação:
- mensagem com link vira link acompanhado do comentário de quem enviou;
- imagem passa pelo OCR em várias passadas, perde os elementos de interface e, se a leitura
  falhar ou tiver confiança baixa, pode ser transcrita por um modelo de visão local;
- página longa é reduzida aos trechos sobre vacinação, e não aos primeiros caracteres;
- texto encaminhado perde emoji, marcadores e chamadas para repassar.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from immunocheck.application.content_normalizer import ContentExtractionError, LinkTextExtractor
from immunocheck.application.input_cleaning import (
    clean_forwarded_text,
    split_message_link,
    strip_interface_lines,
)
from immunocheck.application.passage_selection import DEFAULT_BUDGET, select_claim_passages
from immunocheck.domain.models import ContentKind, ContentSubmission

VISION_CONFIDENCE_THRESHOLD = 70.0
MINIMUM_FALLBACK_WORDS = 3


class OCRReadingLike(Protocol):
    text: str
    mean_confidence: float


class ImageReader(Protocol):
    def read(self, submission: ContentSubmission) -> OCRReadingLike: ...


class VisionTranscriber(Protocol):
    def transcribe(self, submission: ContentSubmission) -> str: ...


def route_message(text: str) -> ContentSubmission:
    """Mensagem com uma URL HTTPS vira link; o restante da mensagem segue como comentário."""

    stripped = text.strip()
    url, commentary = split_message_link(stripped)
    if url is None or not url.lower().startswith("https://"):
        return ContentSubmission(kind=ContentKind.TEXT, text=stripped)
    return ContentSubmission(kind=ContentKind.LINK, url=url, text=commentary or None)


@dataclass(frozen=True, slots=True)
class UnderstandingNormalizer:
    image_reader: ImageReader
    link_extractor: LinkTextExtractor
    vision: VisionTranscriber | None = None
    vision_confidence_threshold: float = VISION_CONFIDENCE_THRESHOLD
    budget: int = DEFAULT_BUDGET

    def normalize(self, submission: ContentSubmission) -> str:
        if submission.kind is ContentKind.TEXT and submission.text is not None:
            return _one_line(_require_text(clean_forwarded_text(submission.text)))
        if submission.kind is ContentKind.IMAGE:
            content = self._bounded(self._image_text(submission))
            return _with_note(content, submission.text, "Legenda enviada com a imagem")
        if submission.kind is ContentKind.LINK and submission.url is not None:
            return self._link_text(submission)
        raise ContentExtractionError("O tipo de conteúdo não pôde ser normalizado.")

    def _image_text(self, submission: ContentSubmission) -> str:
        failure: ContentExtractionError | None = None
        text, confidence = None, 0.0
        try:
            reading = self.image_reader.read(submission)
            text, confidence = strip_interface_lines(reading.text), reading.mean_confidence
        except ContentExtractionError as exc:
            failure = exc
        if self.vision is not None and (text is None or confidence < self.vision_confidence_threshold):
            try:
                transcribed = strip_interface_lines(self.vision.transcribe(submission))
                if len(transcribed.split()) >= MINIMUM_FALLBACK_WORDS:
                    return transcribed
            except ContentExtractionError:
                pass
        if text is None:
            caption = clean_forwarded_text(submission.text or "")
            if len(caption.split()) >= MINIMUM_FALLBACK_WORDS:
                return caption
            raise failure or ContentExtractionError("A imagem não pôde ser lida.")
        return text

    def _link_text(self, submission: ContentSubmission) -> str:
        commentary = clean_forwarded_text(submission.text or "")
        try:
            page = self._bounded(self.link_extractor.extract(submission.url or ""))
        except ContentExtractionError:
            # Link inacessível: o comentário pode conter a própria alegação.
            if len(commentary.split()) >= MINIMUM_FALLBACK_WORDS:
                return _one_line(commentary)
            raise
        if not commentary:
            return page
        return f"Mensagem de quem enviou: {_one_line(commentary)}\n\nConteúdo do link:\n{page}"

    def _bounded(self, text: str) -> str:
        return select_claim_passages(text, self.budget)[0]


def _with_note(content: str, note: str | None, label: str) -> str:
    cleaned = _one_line(clean_forwarded_text(note or ""))
    if not cleaned or cleaned in content:
        return content
    return f"{label}: {cleaned}\n\nTexto da imagem:\n{content}"


def _require_text(text: str) -> str:
    if not text.strip():
        raise ContentExtractionError("A mensagem não contém texto verificável.")
    return text


def _one_line(text: str) -> str:
    return " ".join(text.split())
