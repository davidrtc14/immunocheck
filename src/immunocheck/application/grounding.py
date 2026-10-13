"""D1: ancoragem verificável. O LLM cita trechos literais; o código confere por substring."""

from __future__ import annotations

import copy
import re
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from typing import Any

from immunocheck.application.ports import VerdictGenerator
from immunocheck.application.text_components import StructuredChatClient
from immunocheck.domain.models import DraftVerdict, Evidence, ExtractedClaim, Verdict

MIN_QUOTE_CHARS = 20
MAX_SPANS = 6
SPAN_FIELDS = ("explanation", "correct_fact", "omitted_or_distorted")
UNGROUNDED_EXPLANATION = (
    "As fontes consultadas não permitem sustentar uma conclusão com trechos verificáveis."
)

SUPPORT_SPANS_SCHEMA: dict[str, Any] = {
    "type": "array",
    "maxItems": MAX_SPANS,
    "items": {
        "type": "object",
        "properties": {
            "field": {"type": "string", "enum": list(SPAN_FIELDS)},
            "quote": {"type": "string", "minLength": 1, "maxLength": 400},
        },
        "required": ["field", "quote"],
        "additionalProperties": False,
    },
}

GROUNDING_INSTRUCTION = (
    "\n\nAlém dos demais campos, preencha support_spans com objetos {field, quote}. Cada quote "
    "deve ser um trecho LITERAL, copiado sem nenhuma alteração e com pelo menos 20 caracteres, de "
    "uma das evidências que você citou e que sustente o campo indicado em field "
    "(explanation, correct_fact ou omitted_or_distorted). Forneça ao menos um trecho para "
    "explanation e um para cada campo corretivo não nulo. Nunca invente nem parafraseie trechos; "
    "se não houver trecho literal que sustente o campo, deixe a lista vazia."
)

_NUMBER = re.compile(r"\d[\d.,]*\d|\d")


@dataclass(frozen=True, slots=True)
class GroundingReport:
    grounded: bool
    missing_fields: tuple[str, ...] = ()
    unsupported_numbers: tuple[str, ...] = ()


def alnum_key(text: str) -> str:
    """Remove acentos, pontuação e espaços: tolera hifenização e quebras do texto extraído."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in decomposed if ch.isalnum() and not unicodedata.combining(ch))


def verify_grounding(
    draft: DraftVerdict,
    evidence: Sequence[Evidence],
    spans: Sequence[dict[str, Any]],
) -> GroundingReport:
    """Exige trecho literal por campo gerado e números presentes nos chunks citados."""
    if draft.verdict is Verdict.INSUFFICIENT_EVIDENCE:
        return GroundingReport(grounded=True)
    cited = {item.chunk_id: item for item in evidence if item.chunk_id in set(draft.source_ids)}
    if not cited:
        return GroundingReport(grounded=False, missing_fields=("source_ids",))
    cited_key = alnum_key(" ".join(item.text for item in cited.values()))

    verified_fields: set[str] = set()
    for span in spans:
        if not isinstance(span, dict):
            continue
        field, quote = span.get("field"), span.get("quote")
        if field not in SPAN_FIELDS or not isinstance(quote, str):
            continue
        key = alnum_key(quote)
        if len(key) >= MIN_QUOTE_CHARS and key in cited_key:
            verified_fields.add(field)

    required = ["explanation"]
    if draft.verdict is Verdict.REFUTED:
        required.append("correct_fact")
    if draft.verdict is Verdict.MISLEADING:
        required.append("omitted_or_distorted")
    missing = tuple(field for field in required if field not in verified_fields)

    unsupported: list[str] = []
    generated = " ".join(
        text
        for text in (draft.explanation, draft.correct_fact, draft.omitted_or_distorted)
        if text
    )
    for number in _NUMBER.findall(generated):
        digits = alnum_key(number)
        if len(digits) >= 2 and digits not in cited_key and number not in unsupported:
            unsupported.append(number)
    return GroundingReport(
        grounded=not missing and not unsupported,
        missing_fields=missing,
        unsupported_numbers=tuple(unsupported),
    )


def downgrade(draft: DraftVerdict) -> DraftVerdict:
    """Rebaixa para abstenção preservando as fontes apenas como consultadas."""
    return replace(
        draft,
        verdict=Verdict.INSUFFICIENT_EVIDENCE,
        explanation=UNGROUNDED_EXPLANATION,
        correct_fact=None,
        omitted_or_distorted=None,
    )


class _SpanCapturingClient:
    """Adiciona support_spans ao schema/prompt e guarda a resposta para verificação."""

    def __init__(self, delegate: StructuredChatClient) -> None:
        self._delegate = delegate
        self.spans: list[dict[str, Any]] = []

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        extended = copy.deepcopy(schema)
        extended["properties"]["support_spans"] = SUPPORT_SPANS_SCHEMA
        extended["required"] = [*extended["required"], "support_spans"]
        payload = self._delegate.chat(
            system_prompt=system_prompt + GROUNDING_INSTRUCTION,
            user_prompt=user_prompt,
            schema=extended,
            max_output_tokens=max_output_tokens + 256,
        )
        raw = payload.get("support_spans")
        self.spans = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
        return payload


@dataclass(frozen=True, slots=True)
class GroundedVerdictGenerator:
    """Envolve um gerador congelado da v3 e rebaixa conclusões sem ancoragem literal."""

    client: StructuredChatClient
    factory: Callable[[StructuredChatClient], VerdictGenerator]

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        capture = _SpanCapturingClient(self.client)
        draft = self.factory(capture).generate(claim, evidence)
        report = verify_grounding(draft, evidence, capture.spans)
        return draft if report.grounded else downgrade(draft)
