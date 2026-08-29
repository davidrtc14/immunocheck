import pytest

from immunocheck.ingestion.downloader import (
    DownloadError,
    _read_limited,
    _validate_content,
    _validate_url,
)


class FakeResponse:
    def __init__(self, content: bytes) -> None:
        self._content = content
        self._position = 0

    def read(self, size: int) -> bytes:
        chunk = self._content[self._position : self._position + size]
        self._position += len(chunk)
        return chunk


def test_url_policy_accepts_official_subdomain() -> None:
    _validate_url("https://www.gov.br/saude/manual.pdf", ("gov.br",))


@pytest.mark.parametrize(
    "url",
    (
        "http://www.gov.br/saude/manual.pdf",
        "https://gov.br.evil.example/manual.pdf",
        "https://user:password@www.gov.br/manual.pdf",
    ),
)
def test_url_policy_rejects_unsafe_url(url: str) -> None:
    with pytest.raises(DownloadError):
        _validate_url(url, ("gov.br",))


def test_limited_reader_rejects_oversized_content() -> None:
    response = FakeResponse(b"123456")

    with pytest.raises(DownloadError, match="excede"):
        _read_limited(response, max_bytes=5)


@pytest.mark.parametrize(
    ("expected_format", "content_type", "content"),
    (
        ("pdf", "application/pdf", b"%PDF-1.7 document"),
        ("pdf", "application/octet-stream", b"%PDF-1.4 document"),
        ("html", "text/html", b"<!doctype html><title>Documento</title>"),
        ("html", "application/xhtml+xml", b"<html></html>"),
    ),
)
def test_content_policy_accepts_matching_documents(
    expected_format: str,
    content_type: str,
    content: bytes,
) -> None:
    _validate_content(expected_format, content_type, content)


@pytest.mark.parametrize(
    ("expected_format", "content_type", "content"),
    (
        ("pdf", "text/html", b"<html>erro</html>"),
        ("pdf", "application/pdf", b"not a pdf"),
        ("html", "application/pdf", b"%PDF-1.7 document"),
        ("html", "application/json", b"{}"),
        ("pdf", "application/pdf", b""),
    ),
)
def test_content_policy_rejects_mismatches(
    expected_format: str,
    content_type: str,
    content: bytes,
) -> None:
    with pytest.raises(DownloadError):
        _validate_content(expected_format, content_type, content)
