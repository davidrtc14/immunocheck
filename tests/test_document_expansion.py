from __future__ import annotations

import pytest

from immunocheck.domain.models import Evidence
from immunocheck.retrieval.document_expansion import expand_document_candidates


def _evidence(document: str, page: int, chunk: int) -> Evidence:
    return Evidence(
        chunk_id=f"{document}:p{page}:c{chunk}:abc123",
        text=f"Trecho {chunk}",
        source_name="Fonte",
        document_title="Documento",
        url="https://example.org/doc",
        page=page,
    )


def test_expands_seed_with_first_chunks_and_same_page_neighbors() -> None:
    corpus = tuple(_evidence("doc", 1, index) for index in range(1, 8))

    result = expand_document_candidates(
        corpus,
        (corpus[5].chunk_id,),
        first_chunks=2,
        neighbor_radius=1,
    )

    assert [item.chunk_id for item in result] == [
        corpus[5].chunk_id,
        corpus[0].chunk_id,
        corpus[1].chunk_id,
        corpus[4].chunk_id,
        corpus[6].chunk_id,
    ]


def test_expansion_deduplicates_and_respects_limit() -> None:
    corpus = tuple(_evidence("doc", 1, index) for index in range(1, 8))

    result = expand_document_candidates(
        corpus,
        (corpus[0].chunk_id, corpus[1].chunk_id),
        first_chunks=4,
        neighbor_radius=1,
        max_candidates=3,
    )

    assert len(result) == len({item.chunk_id for item in result}) == 3
    assert result[:2] == corpus[:2]


def test_expansion_rejects_unknown_seed_or_invalid_id() -> None:
    corpus = (_evidence("doc", 1, 1),)

    with pytest.raises(ValueError, match="ausente"):
        expand_document_candidates(corpus, ("doc:p1:c2:missing",))
    with pytest.raises(ValueError, match="incompatível"):
        expand_document_candidates(
            (
                Evidence(
                    chunk_id="invalid",
                    text="Trecho",
                    source_name="Fonte",
                    document_title="Documento",
                    url="https://example.org/doc",
                ),
            ),
            ("invalid",),
        )
