from __future__ import annotations

from collections.abc import Sequence

import pytest

from immunocheck.domain.models import Evidence
from immunocheck.retrieval.neighbor_context import (
    NeighborContextRetriever,
    document_id,
    overlap_length,
)


def _chunk(chunk_id: str, text: str) -> Evidence:
    return Evidence(chunk_id, text, "MS", "Manual", "https://example.org")


CORPUS = (
    _chunk("a:p1:c1:h1", "Primeiro trecho. A vacina é aplicada aos 2 meses."),
    _chunk("a:p1:c2:h2", "aos 2 meses. O reforço ocorre aos 15 meses de idade."),
    _chunk("a:p2:c3:h3", "de idade. Gestantes devem receber a dTpa."),
    _chunk("b:p1:c1:h4", "Outro documento sem relação."),
)


class _Base:
    def __init__(self, evidence: Sequence[Evidence]) -> None:
        self.evidence = tuple(evidence)
        self.queries: list[Sequence[str]] = []

    def retrieve_queries(self, queries: Sequence[str]) -> tuple[Evidence, ...]:
        self.queries.append(queries)
        return self.evidence


def test_overlap_and_document_id() -> None:
    assert overlap_length("abc aos 2 meses.", "aos 2 meses. O reforço") == len("aos 2 meses.")
    assert overlap_length("abc", "xyz") == 0
    assert document_id("a:p1:c2:h2") == "a"


def test_middle_chunk_gets_both_neighbors_without_overlap() -> None:
    retriever = NeighborContextRetriever(_Base([CORPUS[1]]), CORPUS)
    (expanded,) = retriever.retrieve_queries(["reforço"])
    assert expanded.text == (
        "Primeiro trecho. A vacina é aplicada "
        "aos 2 meses. O reforço ocorre aos 15 meses de idade. "
        "Gestantes devem receber a dTpa."
    )
    assert expanded.chunk_id == "a:p1:c2:h2" and expanded.url == CORPUS[1].url


def test_neighbors_stay_inside_the_document() -> None:
    retriever = NeighborContextRetriever(_Base([CORPUS[2], CORPUS[3]]), CORPUS)
    last_of_a, only_b = retriever.retrieve_queries(["dTpa"])
    assert last_of_a.text.endswith("Gestantes devem receber a dTpa.")
    assert "Outro documento" not in last_of_a.text
    assert only_b.text == CORPUS[3].text


def test_long_neighbors_are_cut_at_word_boundaries() -> None:
    corpus = (
        _chunk("d:p1:c1:h1", "palavra " * 100 + "final do anterior."),
        _chunk("d:p1:c2:h2", "Centro."),
        _chunk("d:p1:c3:h3", "início do seguinte " + "termo " * 100),
    )
    retriever = NeighborContextRetriever(_Base([corpus[1]]), corpus, neighbor_chars=40)
    (expanded,) = retriever.retrieve_queries(["centro"])
    before, after = expanded.text.split(" Centro. ")
    assert before.startswith("[…] ") and before.endswith("final do anterior.")
    assert after.startswith("início do seguinte") and after.endswith(" […]")
    assert len(before) <= 40 + 4 and len(after) <= 40 + 4


def test_invalid_neighbor_chars() -> None:
    with pytest.raises(ValueError):
        NeighborContextRetriever(_Base([]), CORPUS, neighbor_chars=0)
