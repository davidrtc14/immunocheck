from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from functools import cached_property
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.rrf import Retriever

BGE_RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
BGE_RERANKER_REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"
RERANK_CANDIDATE_DEPTH = 20
RERANK_OUTPUT_DEPTH = 10
RERANK_MAX_LENGTH = 512


class RerankerError(RuntimeError):
    """Indica falha ou saída inconsistente do modelo de reranking."""


class PairScorer(Protocol):
    def score(self, query: str, passages: Sequence[str]) -> NDArray[np.float32]: ...


class SentenceTransformerCrossEncoderScorer:
    def __init__(
        self,
        *,
        model_name: str = BGE_RERANKER_MODEL,
        revision: str = BGE_RERANKER_REVISION,
        cache_folder: Path | None = None,
        device: str = "cpu",
        batch_size: int = 4,
        max_length: int = RERANK_MAX_LENGTH,
        local_files_only: bool = False,
        show_progress_bar: bool = False,
    ) -> None:
        if device != "cpu":
            raise ValueError("A configuração experimental mantém o reranker na CPU.")
        if batch_size <= 0 or max_length <= 0:
            raise ValueError("batch_size e max_length devem ser positivos.")
        self.model_name = model_name
        self.revision = revision
        self.cache_folder = cache_folder
        self.device = device
        self.batch_size = batch_size
        self.max_length = max_length
        self.local_files_only = local_files_only
        self.show_progress_bar = show_progress_bar

    @cached_property
    def _model(self):
        from sentence_transformers import CrossEncoder

        return CrossEncoder(
            self.model_name,
            device=self.device,
            cache_folder=str(self.cache_folder) if self.cache_folder else None,
            trust_remote_code=False,
            revision=self.revision,
            local_files_only=self.local_files_only,
            max_length=self.max_length,
        )

    def score(self, query: str, passages: Sequence[str]) -> NDArray[np.float32]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("A consulta do reranker deve ser uma string não vazia.")
        normalized_passages = tuple(passages)
        if any(
            not isinstance(passage, str) or not passage.strip() for passage in normalized_passages
        ):
            raise ValueError("Todos os trechos do reranker devem ser strings não vazias.")
        if not normalized_passages:
            return np.empty(0, dtype=np.float32)

        scores = self._model.predict(
            [(query, passage) for passage in normalized_passages],
            batch_size=self.batch_size,
            show_progress_bar=self.show_progress_bar,
            convert_to_numpy=True,
        )
        array = np.asarray(scores, dtype=np.float32).reshape(-1)
        if array.shape != (len(normalized_passages),) or not np.all(np.isfinite(array)):
            raise RerankerError("O modelo retornou scores inválidos.")
        return array


def rerank_evidence(
    query: str,
    candidates: Sequence[Evidence],
    scorer: PairScorer,
    *,
    top_k: int = RERANK_OUTPUT_DEPTH,
) -> tuple[Evidence, ...]:
    if top_k <= 0:
        raise ValueError("top_k deve ser positivo.")
    if not candidates:
        return ()
    if len({item.chunk_id for item in candidates}) != len(candidates):
        raise RerankerError("Os candidatos do reranker contêm chunk_id duplicado.")

    scores = np.asarray(
        scorer.score(query, tuple(item.text for item in candidates)),
        dtype=np.float32,
    ).reshape(-1)
    if scores.shape != (len(candidates),) or not np.all(np.isfinite(scores)):
        raise RerankerError("O scorer retornou quantidade ou valores inválidos.")
    ranked = sorted(
        enumerate(scores),
        key=lambda item: (-float(item[1]), item[0]),
    )
    return tuple(
        replace(candidates[index], retrieval_score=float(score)) for index, score in ranked[:top_k]
    )


class RerankingRetriever:
    def __init__(
        self,
        base_retriever: Retriever,
        scorer: PairScorer,
        *,
        top_k: int = RERANK_OUTPUT_DEPTH,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        self._base_retriever = base_retriever
        self._scorer = scorer
        self._top_k = top_k

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        candidates = tuple(self._base_retriever.retrieve(claim))
        return rerank_evidence(claim.text, candidates, self._scorer, top_k=self._top_k)
