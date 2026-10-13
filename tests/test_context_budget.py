from __future__ import annotations

import json
from typing import Any

import pytest

from immunocheck.application.content_normalizer import (
    MAX_EXTRACTED_CHARS,
    MultimodalNormalizer,
)
from immunocheck.domain.models import ContentKind, ContentSubmission
from immunocheck.infrastructure.context_budget import (
    TRUNCATION_MARK,
    ContextBudgetClient,
    ContextBudgetError,
)
from immunocheck.infrastructure.ollama import OllamaError

SCHEMA = {"type": "object"}


class Recorder:
    def __init__(self) -> None:
        self.user_prompts: list[str] = []

    def chat(self, *, system_prompt, user_prompt, schema, max_output_tokens) -> dict[str, Any]:
        self.user_prompts.append(user_prompt)
        return {"ok": True}


def _call(client: ContextBudgetClient, user_prompt: str, out: int = 96) -> None:
    client.chat(
        system_prompt="Sistema.",
        user_prompt=user_prompt,
        schema=SCHEMA,
        max_output_tokens=out,
    )


def _prompt(texts: list[str]) -> str:
    return json.dumps(
        {
            "claim": "Alegação.",
            "evidence": [{"ref": f"E{i}", "text": text} for i, text in enumerate(texts, 1)],
        },
        ensure_ascii=False,
    )


def test_prompt_within_budget_is_unchanged() -> None:
    recorder = Recorder()
    prompt = _prompt(["curto"] * 3)
    _call(ContextBudgetClient(recorder), prompt)
    assert recorder.user_prompts == [prompt]


def test_oversized_evidence_is_truncated_per_chunk_and_fits() -> None:
    recorder = Recorder()
    client = ContextBudgetClient(recorder)
    texts = ["palavra " * 400] * 20 + ["trecho curto preservado"]
    _call(client, _prompt(texts))

    sent = recorder.user_prompts[0]
    budget = int((8_192 - 96 - 256) * 2.8) - len("Sistema.") - len(json.dumps(SCHEMA))
    assert len(sent) <= budget
    evidence = json.loads(sent)["evidence"]
    assert len(evidence) == 21
    assert evidence[-1]["text"] == "trecho curto preservado"
    assert all(item["text"].endswith(TRUNCATION_MARK) for item in evidence[:20])
    assert json.loads(sent)["claim"] == "Alegação."


def test_long_user_text_is_truncated_for_extractor() -> None:
    recorder = Recorder()
    prompt = json.dumps({"texto_do_usuario": "a " * 30_000})
    _call(ContextBudgetClient(recorder), prompt, out=192)
    assert len(recorder.user_prompts[0]) < len(prompt)


def test_untruncatable_or_hopeless_prompts_fail_closed() -> None:
    client = ContextBudgetClient(Recorder(), context_tokens=1_000, min_chunk_chars=300)
    with pytest.raises(ContextBudgetError):
        _call(client, "x" * 10_000)
    with pytest.raises(OllamaError):
        _call(client, _prompt(["y" * 400] * 40))


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(ValueError):
        ContextBudgetClient(Recorder(), context_tokens=0)


class _Extractor:
    def __init__(self, text: str) -> None:
        self.text = text

    def extract(self, value: object) -> str:
        return self.text


def test_multimodal_normalizer_bounds_link_and_ocr_text() -> None:
    long_text = "palavra " * 10_000
    normalizer = MultimodalNormalizer(_Extractor(long_text), _Extractor(long_text))
    link = ContentSubmission(kind=ContentKind.LINK, url="https://example.org/a")
    image = ContentSubmission(kind=ContentKind.IMAGE, data=b"x")
    assert len(normalizer.normalize(link)) <= MAX_EXTRACTED_CHARS
    assert len(normalizer.normalize(image)) <= MAX_EXTRACTED_CHARS
    short = MultimodalNormalizer(_Extractor("curto"), _Extractor("curto"))
    assert short.normalize(link) == "curto"
