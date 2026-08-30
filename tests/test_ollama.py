import json

import pytest

from immunocheck.infrastructure.ollama import (
    OllamaError,
    OllamaStructuredClient,
    _parse_structured_response,
)


@pytest.mark.parametrize(
    "base_url",
    (
        "https://127.0.0.1:11434",
        "http://ollama.example:11434",
        "http://localhost.evil.example:11434",
        "http://user:password@localhost:11434",
        "http://localhost:11434/api",
        "http://localhost:invalid",
    ),
)
def test_client_rejects_non_local_or_malformed_base_url(base_url: str) -> None:
    with pytest.raises(ValueError):
        OllamaStructuredClient(base_url=base_url)


def test_client_rejects_non_positive_context_or_output_limit() -> None:
    with pytest.raises(ValueError, match="contexto"):
        OllamaStructuredClient(context_tokens=0)

    with pytest.raises(ValueError, match="tokens"):
        OllamaStructuredClient().chat(
            system_prompt="system",
            user_prompt="user",
            schema={"type": "object"},
            max_output_tokens=0,
        )


def test_parser_extracts_structured_message_content() -> None:
    content = {"verdict": "SUPPORTED"}
    envelope = {"message": {"content": json.dumps(content)}}

    parsed = _parse_structured_response(json.dumps(envelope).encode())

    assert parsed == content


@pytest.mark.parametrize(
    "response",
    (
        b"not-json",
        b"{}",
        json.dumps({"done_reason": "length", "message": {"content": "{}"}}).encode(),
        json.dumps({"message": {"content": "[]"}}).encode(),
    ),
)
def test_parser_rejects_invalid_envelope_or_content(response: bytes) -> None:
    with pytest.raises(OllamaError):
        _parse_structured_response(response)
