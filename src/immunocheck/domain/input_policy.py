from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

from immunocheck.domain.models import ContentKind, ContentSubmission


class InvalidSubmissionError(ValueError):
    """Indica que uma entrada viola os limites públicos do sistema."""


@dataclass(frozen=True, slots=True)
class InputLimits:
    max_text_chars: int = 4_096
    max_image_bytes: int = 10 * 1024 * 1024
    max_image_pixels: int = 12_000_000
    max_url_chars: int = 2_048
    allowed_image_types: frozenset[str] = frozenset({"image/jpeg", "image/png", "image/webp"})


def validate_submission(
    submission: ContentSubmission,
    limits: InputLimits | None = None,
) -> None:
    limits = limits or InputLimits()
    if submission.kind is ContentKind.TEXT:
        _validate_text(submission, limits)
        return
    if submission.kind is ContentKind.IMAGE:
        _validate_image(submission, limits)
        return
    if submission.kind is ContentKind.LINK:
        _validate_link(submission, limits)
        return
    raise InvalidSubmissionError("Tipo de conteúdo não aceito.")


def _validate_text(submission: ContentSubmission, limits: InputLimits) -> None:
    if submission.text is None or not submission.text.strip():
        raise InvalidSubmissionError("Envie um texto não vazio.")
    if len(submission.text) > limits.max_text_chars:
        raise InvalidSubmissionError(
            f"O texto excede o limite de {limits.max_text_chars} caracteres."
        )


def _validate_image(submission: ContentSubmission, limits: InputLimits) -> None:
    if not submission.data:
        raise InvalidSubmissionError("A imagem não contém dados.")
    if submission.media_type not in limits.allowed_image_types:
        raise InvalidSubmissionError("Formato de imagem não aceito.")
    if len(submission.data) > limits.max_image_bytes:
        raise InvalidSubmissionError("A imagem excede o limite de 10 MB.")
    if submission.width is None or submission.height is None:
        raise InvalidSubmissionError("As dimensões da imagem não foram informadas.")
    if submission.width <= 0 or submission.height <= 0:
        raise InvalidSubmissionError("As dimensões da imagem são inválidas.")
    if submission.width * submission.height > limits.max_image_pixels:
        raise InvalidSubmissionError("A imagem excede o limite de 12 megapixels.")


def _validate_link(submission: ContentSubmission, limits: InputLimits) -> None:
    if submission.url is None or not submission.url.strip():
        raise InvalidSubmissionError("Envie uma URL não vazia.")
    if len(submission.url) > limits.max_url_chars:
        raise InvalidSubmissionError("A URL excede o limite permitido.")
    parsed = urlsplit(submission.url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise InvalidSubmissionError("Apenas URLs HTTPS públicas são aceitas.")
    if parsed.username or parsed.password:
        raise InvalidSubmissionError("URLs com credenciais embutidas não são aceitas.")
