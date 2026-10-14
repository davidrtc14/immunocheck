"""Conjunto de paráfrases v5: rótulo herdado do item-pai e métricas de consistência."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from immunocheck.evaluation.end_to_end import EndToEndItem

PARAPHRASE_STYLES = ("colloquial", "formal")
ORIGINAL_FORM = "original"

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
# "covid-19" e "covid" nomeiam a mesma doença; o sufixo não é um dado da alegação.
_DISEASE_NAME_DIGITS = re.compile(r"covid-19", re.IGNORECASE)
_TOKEN = re.compile(r"\w+", re.UNICODE)
_NEGATION_TOKENS = frozenset({"nao", "nunca", "jamais", "nenhum", "nenhuma", "nem", "sem", "zero"})
_UNIVERSAL_TOKENS = frozenset(
    {"todo", "toda", "todos", "todas", "qualquer", "quaisquer", "sempre", "nunca", "jamais"}
)
_RESTRICTIVE_TOKENS = frozenset(
    {"apenas", "somente", "so", "exclusivamente", "exclusiva", "unica", "unico"}
)


class ParaphraseSetError(ValueError):
    """Conjunto de paráfrases inválido."""


@dataclass(frozen=True, slots=True)
class ParaphraseItem:
    paraphrase_id: str
    parent_item_id: str
    style: str
    claim: str
    label: str
    split: str
    claim_family: str


def load_paraphrases(path: Path) -> list[ParaphraseItem]:
    items: list[ParaphraseItem] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                items.append(
                    ParaphraseItem(
                        paraphrase_id=str(payload["paraphrase_id"]),
                        parent_item_id=str(payload["parent_item_id"]),
                        style=str(payload["style"]),
                        claim=str(payload["claim"]),
                        label=str(payload["label"]),
                        split=str(payload["split"]),
                        claim_family=str(payload["claim_family"]),
                    )
                )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ParaphraseSetError(f"Linha {line_number} inválida.") from exc
    return items


def validate_paraphrases(
    paraphrases: Sequence[ParaphraseItem],
    parents: Sequence[EndToEndItem],
) -> None:
    """Exige duas paráfrases por item, rótulo herdado e preservação de marcadores materiais."""

    by_parent = {item.item_id: item for item in parents}
    seen_ids: set[str] = set()
    styles_by_parent: dict[str, set[str]] = defaultdict(set)
    for paraphrase in paraphrases:
        if paraphrase.paraphrase_id in seen_ids:
            raise ParaphraseSetError(f"ID repetido: {paraphrase.paraphrase_id}.")
        seen_ids.add(paraphrase.paraphrase_id)
        parent = by_parent.get(paraphrase.parent_item_id)
        if parent is None:
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: item-pai inexistente.")
        if paraphrase.style not in PARAPHRASE_STYLES:
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: estilo inválido.")
        if paraphrase.style in styles_by_parent[parent.item_id]:
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: estilo repetido.")
        styles_by_parent[parent.item_id].add(paraphrase.style)
        if (
            paraphrase.label != parent.label.value
            or paraphrase.split != parent.split.value
            or paraphrase.claim_family != parent.claim_family
        ):
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: metadados divergem do pai.")
        if _normalized(paraphrase.claim) == _normalized(parent.claim):
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: texto idêntico ao pai.")
        _require_material_markers(paraphrase, parent.claim)
    missing = [
        item.item_id for item in parents if styles_by_parent[item.item_id] != set(PARAPHRASE_STYLES)
    ]
    if missing:
        raise ParaphraseSetError(f"Itens sem as duas paráfrases: {', '.join(missing[:5])}.")


def consistency_rate(predictions: Mapping[str, Mapping[str, str | None]]) -> float:
    """Fração de itens cujo veredito é idêntico em todas as formas (falha conta como divergente)."""

    if not predictions:
        raise ValueError("Nenhuma predição para medir consistência.")
    expected_forms = {ORIGINAL_FORM, *PARAPHRASE_STYLES}
    consistent = 0
    for item_id, by_form in predictions.items():
        if set(by_form) != expected_forms:
            raise ValueError(f"{item_id}: formas incompletas.")
        verdicts = set(by_form.values())
        if None not in verdicts and len(verdicts) == 1:
            consistent += 1
    return consistent / len(predictions)


def _require_material_markers(paraphrase: ParaphraseItem, parent_claim: str) -> None:
    parent_numbers = _numbers(parent_claim)
    missing_numbers = parent_numbers - _numbers(paraphrase.claim)
    if missing_numbers:
        raise ParaphraseSetError(
            f"{paraphrase.paraphrase_id}: números ausentes {sorted(missing_numbers)}."
        )
    parent_tokens = _tokens(parent_claim)
    tokens = _tokens(paraphrase.claim)
    for name, group in (
        ("negação", _NEGATION_TOKENS),
        ("quantificador universal", _UNIVERSAL_TOKENS),
        ("restrição", _RESTRICTIVE_TOKENS),
    ):
        if parent_tokens & group and not tokens & group:
            raise ParaphraseSetError(f"{paraphrase.paraphrase_id}: {name} não preservada.")


def _numbers(text: str) -> set[str]:
    text = _DISEASE_NAME_DIGITS.sub("covid", text)
    return {match.replace(".", "").replace(",", ".") for match in _NUMBER.findall(text)}


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(_normalized(text)))


def _normalized(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char)).strip()
