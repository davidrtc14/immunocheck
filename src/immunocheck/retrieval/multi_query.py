"""v5: recuperação por várias consultas (alegação canônica, proposições, inglês) com RRF."""

from __future__ import annotations

from collections.abc import Sequence

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.reranker import PairScorer, rerank_evidence
from immunocheck.retrieval.rrf import Retriever, reciprocal_rank_fusion

DEFAULT_RANK_CONSTANT = 60
DEFAULT_RERANK_DEPTH = 20


class MultiQueryRetriever:
    """Funde rankings densos de várias consultas; com uma consulta preserva o ranking original."""

    def __init__(
        self,
        base: Retriever,
        *,
        top_k: int = 8,
        rank_constant: int = DEFAULT_RANK_CONSTANT,
        scorer: PairScorer | None = None,
        rerank_depth: int = DEFAULT_RERANK_DEPTH,
    ) -> None:
        if top_k <= 0 or rank_constant <= 0 or rerank_depth < top_k:
            raise ValueError("top_k, rank_constant e rerank_depth são inválidos.")
        self._base = base
        self._top_k = top_k
        self._rank_constant = rank_constant
        self._scorer = scorer
        self._rerank_depth = rerank_depth

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        return self.retrieve_queries((claim.text,))

    def retrieve_queries(self, queries: Sequence[str]) -> tuple[Evidence, ...]:
        unique = tuple(dict.fromkeys(query.strip() for query in queries if query.strip()))
        if not unique:
            raise ValueError("A recuperação exige ao menos uma consulta.")
        rankings = tuple(
            tuple(self._base.retrieve(ExtractedClaim(text=query, confidence=1.0)))
            for query in unique
        )
        depth = self._rerank_depth if self._scorer is not None else self._top_k
        if len(rankings) == 1:
            candidates = rankings[0][:depth]
        else:
            candidates = reciprocal_rank_fusion(
                rankings, top_k=depth, rank_constant=self._rank_constant
            )
        if self._scorer is None:
            return tuple(candidates)
        return rerank_evidence(unique[0], candidates, self._scorer, top_k=self._top_k)
