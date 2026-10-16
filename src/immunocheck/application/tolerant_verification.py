"""v6: pós-regras da v5 com verificação tolerante de trecho e de números (ADR-051, Adendo 1).

A v5 rebaixa para NOT_ADDRESSED o julgamento cujo trecho não é substring exata do chunk citado
ou cuja proposição traz um número ausente da evidência. As duas regras continuam aqui, mas
aceitam variações de forma definidas por princípio:
- o trecho vale se a maior subsequência comum de tokens cobrir pelo menos 90% dele;
- o número vale em qualquer forma equivalente (decimal, milhar, "mil", "por cento", extenso).

O módulo congelado `proposition_nli.py` não é alterado: o julgamento do LLM e a validação do
payload são os mesmos, e só as pós-regras são reaplicadas sobre a resposta registrada.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from immunocheck.application.grounding import MIN_QUOTE_CHARS, alnum_key
from immunocheck.application.proposition_nli import (
    MAX_EVIDENCE,
    DowngradeReason,
    LLMPropositionJudge,
    PropositionJudgment,
    Relation,
)
from immunocheck.application.structured_claim import Proposition
from immunocheck.application.text_components import ModelOutputError, StructuredChatClient
from immunocheck.domain.models import Evidence

QUOTE_TOKEN_COVERAGE = 0.9

_NUMBER = re.compile(r"\d+(?:[.,\s]\d{3})*(?:[.,]\d+)?")
_NAME_DIGITS = re.compile(r"covid-19|sars-cov-2", re.IGNORECASE)
_WORD = re.compile(r"\w+")
_NUMBER_WORDS = {
    "zero": 0,
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cem": 100,
}
_MULTIPLIERS = {"mil": 1_000, "milhao": 1_000_000, "milhoes": 1_000_000}


def quote_matches(quote: str, chunk_text: str) -> bool:
    """Substring exata (regra da v5) ou subsequência de tokens cobrindo ≥ 90% do trecho."""

    quote_key = alnum_key(quote)
    if len(quote_key) < MIN_QUOTE_CHARS:
        return False
    if quote_key in alnum_key(chunk_text):
        return True
    quote_tokens = _tokens(quote)
    chunk_tokens = _tokens(chunk_text)
    if not quote_tokens or not chunk_tokens:
        return False
    return _lcs_length(quote_tokens, chunk_tokens) >= QUOTE_TOKEN_COVERAGE * len(quote_tokens)


def unsupported_numbers(proposition_text: str, evidence_text: str) -> tuple[str, ...]:
    """Números da proposição sem nenhuma forma equivalente na evidência recuperada."""

    available = number_values(evidence_text)
    missing: list[str] = []
    for raw in _NUMBER.findall(_NAME_DIGITS.sub(" ", proposition_text)):
        if len(alnum_key(raw)) < 2:
            continue  # mesma regra da v5: números de um dígito não são checados
        values = _parse_number(raw)
        if values and not values & available and raw not in missing:
            missing.append(raw.strip())
    return tuple(missing)


def number_values(text: str) -> set[float]:
    """Valores numéricos presentes no texto, em dígitos ou por extenso, com multiplicadores."""

    folded = _fold(_NAME_DIGITS.sub(" ", text))
    values: set[float] = set()
    for match in _NUMBER.finditer(folded):
        parsed = _parse_number(match.group(0))
        following = _WORD.findall(folded[match.end() : match.end() + 12])
        multiplier = _MULTIPLIERS.get(following[0], 1) if following else 1
        values |= parsed | {value * multiplier for value in parsed}
    words = _WORD.findall(folded)
    for index, word in enumerate(words):
        if word in _NUMBER_WORDS:
            value = float(_NUMBER_WORDS[word])
            nxt = words[index + 1] if index + 1 < len(words) else ""
            values |= {value, value * _MULTIPLIERS.get(nxt, 1)}
    return values


def apply_tolerant_post_rules(
    proposition: Proposition,
    raw: dict[str, Any],
    aliases: dict[str, Evidence],
) -> PropositionJudgment:
    try:
        model_relation = Relation(raw.get("relation"))
    except ValueError as exc:
        raise ModelOutputError("O NLI retornou relação inválida.") from exc
    if model_relation is Relation.NOT_ADDRESSED:
        return PropositionJudgment(proposition, Relation.NOT_ADDRESSED, model_relation)

    def downgraded(reason: DowngradeReason) -> PropositionJudgment:
        return PropositionJudgment(
            proposition, Relation.NOT_ADDRESSED, model_relation, downgrade_reason=reason
        )

    reference, quote = raw.get("source_ref"), raw.get("quote")
    evidence = aliases.get(reference) if isinstance(reference, str) else None
    if evidence is None or not isinstance(quote, str) or not quote_matches(quote, evidence.text):
        return downgraded(DowngradeReason.NO_VERIFIED_QUOTE)
    retrieved_text = " ".join(item.text for item in aliases.values())
    if model_relation is Relation.ENTAILED and unsupported_numbers(
        proposition.text, retrieved_text
    ):
        return downgraded(DowngradeReason.UNSUPPORTED_NUMBER)
    return PropositionJudgment(
        proposition,
        model_relation,
        model_relation,
        quote=" ".join(quote.split()),
        source_id=evidence.chunk_id,
    )


@dataclass(slots=True)
class _RecordingClient:
    delegate: StructuredChatClient
    payload: dict[str, Any] | None = None

    def chat(self, **kwargs: Any) -> dict[str, Any]:
        self.payload = self.delegate.chat(**kwargs)
        return self.payload


@dataclass(frozen=True, slots=True)
class TolerantPropositionJudge:
    """Mesmo prompt, schema e validação da v5; só as pós-regras são as tolerantes."""

    client: StructuredChatClient
    max_output_tokens: int = 900

    def judge(
        self,
        propositions: Sequence[Proposition],
        evidence: Sequence[Evidence],
        *,
        retry: bool = False,
    ) -> tuple[PropositionJudgment, ...]:
        recorder = _RecordingClient(self.client)
        strict = LLMPropositionJudge(recorder, self.max_output_tokens).judge(
            propositions, evidence, retry=retry
        )
        if recorder.payload is None:  # sem evidência: nada foi perguntado ao LLM
            return strict
        aliases = {f"E{index}": item for index, item in enumerate(evidence[:MAX_EVIDENCE], start=1)}
        by_id = {item["proposition"]: item for item in recorder.payload["judgments"]}
        return tuple(
            apply_tolerant_post_rules(proposition, by_id[f"P{index}"], aliases)
            for index, proposition in enumerate(propositions, start=1)
        )


def _tokens(text: str) -> list[str]:
    return [key for key in (alnum_key(word) for word in text.split()) if key]


def _lcs_length(first: list[str], second: list[str]) -> int:
    previous = [0] * (len(second) + 1)
    for token in first:
        current = [0]
        for column, other in enumerate(second, start=1):
            current.append(
                previous[column - 1] + 1
                if token == other
                else max(previous[column], current[column - 1])
            )
        previous = current
    return previous[-1]


def _parse_number(raw: str) -> set[float]:
    """Leituras possíveis de um número escrito com vírgula, ponto ou espaço.

    Com os dois separadores, o último é o decimal ("1.234,5"). Com um só separador repetido, ele
    é de milhar ("1.000.000"). Com um só separador seguido de exatamente três dígitos, a leitura
    é ambígua ("28.000" ou "2,500") e as duas valem; nos demais casos, ele é decimal ("90,7").
    """

    compact = raw.strip().replace(" ", "")
    separators = [char for char in compact if char in ".,"]
    if not separators:
        return {float(compact)}
    if len(set(separators)) == 2:
        decimal = separators[-1]
        thousands = "." if decimal == "," else ","
        return {float(compact.replace(thousands, "").replace(decimal, "."))}
    separator = separators[0]
    if len(separators) > 1:
        return {float(compact.replace(separator, ""))}
    integer, fraction = compact.split(separator)
    readings = {float(f"{integer}.{fraction}")}
    if len(fraction) == 3:
        readings.add(float(integer + fraction))
    return readings


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))
