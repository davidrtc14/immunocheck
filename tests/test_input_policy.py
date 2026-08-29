import pytest

from immunocheck.domain.input_policy import InvalidSubmissionError, validate_submission
from immunocheck.domain.models import ContentKind, ContentSubmission


def test_rejects_text_above_telegram_limit() -> None:
    submission = ContentSubmission(kind=ContentKind.TEXT, text="a" * 4_097)

    with pytest.raises(InvalidSubmissionError, match="4096"):
        validate_submission(submission)


def test_rejects_non_https_link() -> None:
    submission = ContentSubmission(kind=ContentKind.LINK, url="http://example.com/noticia")

    with pytest.raises(InvalidSubmissionError, match="HTTPS"):
        validate_submission(submission)


def test_accepts_supported_image_within_limits() -> None:
    submission = ContentSubmission(
        kind=ContentKind.IMAGE,
        data=b"image-bytes",
        media_type="image/png",
        width=1_000,
        height=1_000,
    )

    validate_submission(submission)
