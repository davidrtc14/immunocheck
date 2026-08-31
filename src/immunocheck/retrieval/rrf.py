from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from immunocheck.domain.models import Evidence, ExtractedClaim


class Retriever(Protocol):
    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]: ...


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[Evidence]],
    *,
    top_k: int = 10,
    rank_constant: int = 60,
) -> tuple[Evidence, ...]:
    if top_k <= 0 or rank_constant <= 0:
        raise ValueError("top_k e rank_constant devem ser positivos.")
    scores: dict[str, float] = {}
    evidence_by_id: dict[str, Evidence] = {}
    for ranking in rankings:
        seen_in_ranking: set[str] = set()
        for rank, evidence in enumerate(ranking, start=1):
            if evidence.chunk_id in seen_in_ranking:
                continue
            seen_in_ranking.add(evidence.chunk_id)
            evidence_by_id.setdefault(evidence.chunk_id, evidence)
            scores[evidence.chunk_id] = scores.get(evidence.chunk_id, 0.0) + 1.0 / (
                rank_constant + rank
            )
    ranked_ids = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return tuple(
        replace(evidence_by_id[chunk_id], retrieval_score=scores[chunk_id])
        for chunk_id in ranked_ids[:top_k]
    )


class HybridRetriever:
    def __init__(
        self,
        retrievers: Sequence[Retriever],
        *,
        top_k: int = 10,
        rank_constant: int = 60,
    ) -> None:
        if len(retrievers) < 2:
            raise ValueError("O retriever híbrido exige pelo menos dois rankings.")
        if top_k <= 0 or rank_constant <= 0:
            raise ValueError("top_k e rank_constant devem ser positivos.")
        self._retrievers = tuple(retrievers)
        self._top_k = top_k
        self._rank_constant = rank_constant

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        rankings = tuple(tuple(retriever.retrieve(claim)) for retriever in self._retrievers)
        return reciprocal_rank_fusion(
            rankings,
            top_k=self._top_k,
            rank_constant=self._rank_constant,
        )
