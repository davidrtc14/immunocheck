"""v7 (ADR-054), candidata C2: cada evidência vai ao juiz com o entorno no documento.

Os chunks do corpus têm ~1.200 caracteres e se sobrepõem em ~200. A frase decisiva às vezes fica
logo antes ou logo depois do chunk recuperado. Este invólucro acrescenta ao texto da evidência o fim
do chunk anterior e o começo do seguinte do mesmo documento, sem a parte sobreposta e dentro de um
teto de caracteres por lado. O `chunk_id` e os metadados continuam os do chunk recuperado, então a
citação exibida ao usuário segue montada pelo corpus.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Sequence
from typing import Protocol

from immunocheck.domain.models import Evidence

DEFAULT_NEIGHBOR_CHARS = 300
ELLIPSIS = "[…] "


class QueryRetriever(Protocol):
    def retrieve_queries(self, queries: Sequence[str]) -> tuple[Evidence, ...]: ...


def document_id(chunk_id: str) -> str:
    return chunk_id.split(":", 1)[0]


def overlap_length(left: str, right: str) -> int:
    """Tamanho do maior sufixo de `left` que é prefixo de `right`."""

    for size in range(min(len(left), len(right)), 0, -1):
        if left.endswith(right[:size]):
            return size
    return 0


def _tail(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text.strip()
    cut = text[-limit:]
    space = cut.find(" ")
    return ELLIPSIS + (cut[space + 1 :] if 0 <= space < len(cut) - 1 else cut).strip()


def _head(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text.strip()
    cut = text[:limit]
    space = cut.rfind(" ")
    return (cut[:space] if space > 0 else cut).strip() + " […]"


class NeighborContextRetriever:
    """Recupera com o retriever de base e amplia cada evidência com os chunks vizinhos."""

    def __init__(
        self,
        base: QueryRetriever,
        corpus: Iterable[Evidence],
        *,
        neighbor_chars: int = DEFAULT_NEIGHBOR_CHARS,
    ) -> None:
        if neighbor_chars <= 0:
            raise ValueError("neighbor_chars deve ser positivo.")
        self._base = base
        self._neighbor_chars = neighbor_chars
        self._previous: dict[str, Evidence] = {}
        self._next: dict[str, Evidence] = {}
        last: Evidence | None = None
        for chunk in corpus:
            if last is not None and document_id(last.chunk_id) == document_id(chunk.chunk_id):
                self._previous[chunk.chunk_id] = last
                self._next[last.chunk_id] = chunk
            last = chunk

    def expand(self, evidence: Evidence) -> Evidence:
        text = evidence.text
        parts = []
        previous = self._previous.get(evidence.chunk_id)
        if previous is not None:
            fresh = previous.text[: len(previous.text) - overlap_length(previous.text, text)]
            if fresh.strip():
                parts.append(_tail(fresh, self._neighbor_chars))
        parts.append(text)
        following = self._next.get(evidence.chunk_id)
        if following is not None:
            fresh = following.text[overlap_length(text, following.text) :]
            if fresh.strip():
                parts.append(_head(fresh, self._neighbor_chars))
        return dataclasses.replace(evidence, text=" ".join(parts))

    def retrieve_queries(self, queries: Sequence[str]) -> tuple[Evidence, ...]:
        return tuple(self.expand(item) for item in self._base.retrieve_queries(queries))
