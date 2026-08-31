from __future__ import annotations

import numpy as np
import pytest

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.reranker import (
    RerankerError,
    RerankingRetriever,
    rerank_evidence,
)


def evidence(chunk_id: str) -> Evidence:
    return Evidence(chunk_id, f"texto {chunk_id}", "fonte", "documento", f"https://{chunk_id}")


class FakeScorer:
    def score(self, query, passages):
        assert query == "alegação"
        assert passages == ("texto a", "texto b", "texto c")
        return np.asarray([0.1, 0.9, 0.4], dtype=np.float32)


class StubRetriever:
    def retrieve(self, claim):
        assert claim.text == "alegação"
        return (evidence("a"), evidence("b"), evidence("c"))


def test_rerank_evidence_orders_by_cross_encoder_score() -> None:
    result = rerank_evidence(
        "alegação",
        (evidence("a"), evidence("b"), evidence("c")),
        FakeScorer(),
        top_k=2,
    )

    assert [item.chunk_id for item in result] == ["b", "c"]
    assert result[0].retrieval_score == pytest.approx(0.9)


def test_reranker_preserves_original_order_on_tie() -> None:
    class TiedScorer:
        def score(self, query, passages):
            del query
            return np.ones(len(passages), dtype=np.float32)

    result = rerank_evidence("alegação", (evidence("b"), evidence("a")), TiedScorer())

    assert [item.chunk_id for item in result] == ["b", "a"]


def test_reranker_rejects_duplicate_or_invalid_scores() -> None:
    with pytest.raises(RerankerError, match="duplicado"):
        rerank_evidence("alegação", (evidence("a"), evidence("a")), FakeScorer())

    class InvalidScorer:
        def score(self, query, passages):
            del query, passages
            return np.asarray([float("nan")])

    with pytest.raises(RerankerError, match="inválidos"):
        rerank_evidence("alegação", (evidence("a"), evidence("b")), InvalidScorer())


def test_reranking_retriever_wraps_base_retriever() -> None:
    retriever = RerankingRetriever(StubRetriever(), FakeScorer(), top_k=1)

    result = retriever.retrieve(ExtractedClaim("alegação", 1.0))

    assert [item.chunk_id for item in result] == ["b"]
