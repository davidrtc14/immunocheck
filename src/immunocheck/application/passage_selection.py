"""Seleção dos trechos de um texto longo que podem conter a alegação sobre vacinação (ADR-050).

Substitui o corte cego nos primeiros caracteres: mantém o título e os parágrafos que mencionam o
tema, na ordem original, até o orçamento. Sem menção ao tema, recai no corte do início.
"""

from __future__ import annotations

import re
import unicodedata

DEFAULT_BUDGET = 6_000

# Raízes genéricas do domínio de vacinação, escritas sem consultar os itens de avaliação.
_TOPIC_STEMS = (
    "vacin", "imuniz", "dose", "reforco", "sarampo", "gripe", "influenza", "covid", "coronav",
    "hpv", "bcg", "polio", "hepatite", "febre amarela", "coqueluche", "tetano", "difteria",
    "rotav", "pneumoc", "meningo", "varicela", "caxumba", "rubeola", "dengue", "anvisa",
    "ministerio da saude", "sus", "efeito colateral", "efeitos colaterais", "reacao adversa",
    "eficacia", "autismo", "mrna", "anticorpo", "imunidade", "pni", "dpni", "triplice",
    "tetravalente", "pentavalente", "hexavalente", "cobertura", "calendario", "surto",
    "epidemi", "pandemi", "virus", "viral", "bacteria",
)
_STEM_PATTERN = re.compile(r"\b(?:" + "|".join(re.escape(stem) for stem in _TOPIC_STEMS) + ")")


def topic_score(text: str) -> int:
    return len(_STEM_PATTERN.findall(_fold(text)))


def select_claim_passages(text: str, budget: int = DEFAULT_BUDGET) -> tuple[str, bool]:
    """Devolve o texto reduzido ao orçamento e se houve redução."""

    if budget <= 0:
        raise ValueError("O orçamento de caracteres deve ser positivo.")
    if len(text) <= budget:
        return text, False
    paragraphs = [paragraph for paragraph in text.splitlines() if paragraph.strip()]
    title, body = paragraphs[0], paragraphs[1:]
    ranked = sorted(
        (index for index, paragraph in enumerate(body) if topic_score(paragraph) > 0),
        key=lambda index: (-topic_score(body[index]), index),
    )
    if not ranked:
        return _cut(text, budget), True
    chosen: set[int] = set()
    used = len(title)
    for index in ranked:
        size = len(body[index]) + 1
        if used + size > budget:
            continue
        chosen.add(index)
        used += size
    if not chosen:
        return _cut(body[ranked[0]], budget), True
    return "\n".join([title, *(body[index] for index in sorted(chosen))]), True


def _cut(text: str, budget: int) -> str:
    cut = text[:budget]
    boundary = cut.rfind(" ")
    return cut[:boundary] if boundary > budget // 2 else cut


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))
