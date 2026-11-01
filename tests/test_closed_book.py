"""Linha de base sem recuperação (ADR-058)."""

from __future__ import annotations

import json

import pytest

from immunocheck.application.closed_book import (
    CLOSED_BOOK_SCHEMA,
    CLOSED_BOOK_SYSTEM_PROMPT,
    ClosedBookPipeline,
)
from immunocheck.application.text_components import ModelOutputError
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict


class FakeClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    def chat(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return self.payload


def _text(value: str) -> ContentSubmission:
    return ContentSubmission(kind=ContentKind.TEXT, text=value)


def test_decides_without_evidence_and_returns_no_sources() -> None:
    client = FakeClient(
        {
            "verdict": "REFUTED",
            "explanation": "Estudos não mostram relação.",
            "correct_fact": "A vacina não causa autismo.",
            "omitted_or_distorted": None,
        }
    )

    result = ClosedBookPipeline(client).run(_text("  A vacina   causa autismo. "))

    assert result.verdict is Verdict.REFUTED
    assert result.correct_fact == "A vacina não causa autismo."
    assert result.sources == ()
    call = client.calls[0]
    assert call["system_prompt"] == CLOSED_BOOK_SYSTEM_PROMPT
    assert call["schema"] == CLOSED_BOOK_SCHEMA
    assert json.loads(call["user_prompt"]) == {"claim": "A vacina causa autismo."}


@pytest.mark.parametrize(
    "payload",
    [{"verdict": "TALVEZ", "explanation": "x"}, {"verdict": "REFUTED", "explanation": " "}, {}],
)
def test_invalid_model_output_is_a_model_error(payload) -> None:
    with pytest.raises(ModelOutputError):
        ClosedBookPipeline(FakeClient(payload)).run(_text("Alegação."))


def test_only_text_is_accepted() -> None:
    with pytest.raises(ValueError, match="texto"):
        ClosedBookPipeline(FakeClient({})).run(_text("   "))
