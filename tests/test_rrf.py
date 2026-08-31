from __future__ import annotations

from dataclasses import dataclass

import pytest

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.rrf import HybridRetriever, reciprocal_rank_fusion


def evidence(chunk_id: str) -> Evidence:
    return Evidence(chunk_id, chunk_id, "source", "document", f"https://{chunk_id}")


def test_rrf_promotes_result_present_in_both_rankings() -> None:
    dense = (evidence("semantic"), evidence("shared"), evidence("dense-only"))
    lexical = (evidence("lexical"), evidence("shared"), evidence("bm25-only"))

    result = reciprocal_rank_fusion((dense, lexical), top_k=3, rank_constant=60)

    assert result[0].chunk_id == "shared"
    assert result[0].retrieval_score == pytest.approx(2 / 62)


def test_rrf_ignores_duplicate_inside_same_ranking() -> None:
    repeated = evidence("same")

    result = reciprocal_rank_fusion(((repeated, repeated), (evidence("other"),)), top_k=2)

    assert result[0].retrieval_score == pytest.approx(1 / 61)


@dataclass
class StubRetriever:
    ranking: tuple[Evidence, ...]

    def retrieve(self, claim: ExtractedClaim):
        del claim
        return self.ranking


def test_hybrid_retriever_fuses_component_results() -> None:
    retriever = HybridRetriever(
        (
            StubRetriever((evidence("dense"), evidence("shared"))),
            StubRetriever((evidence("shared"), evidence("bm25"))),
        ),
        top_k=1,
    )

    result = retriever.retrieve(ExtractedClaim("alegação", 0.9))

    assert result[0].chunk_id == "shared"
