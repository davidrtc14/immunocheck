from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from immunocheck.domain.models import Evidence
from immunocheck.retrieval.dense import DenseIndexError


def maximal_marginal_relevance(
    candidates: Sequence[Evidence],
    vectors_by_id: Mapping[str, NDArray[np.float32]],
    *,
    top_k: int,
    relevance_weight: float = 0.7,
) -> tuple[Evidence, ...]:
    """Seleciona evidências equilibrando relevância densa e não redundância."""
    if top_k <= 0:
        raise ValueError("top_k deve ser positivo.")
    if not 0.0 <= relevance_weight <= 1.0:
        raise ValueError("relevance_weight deve estar entre zero e um.")
    values = tuple(candidates)
    if not values:
        return ()
    if len({item.chunk_id for item in values}) != len(values):
        raise DenseIndexError("Os candidatos MMR contêm chunk_id duplicado.")

    vectors = []
    relevance = []
    for item in values:
        vector = vectors_by_id.get(item.chunk_id)
        if vector is None:
            raise DenseIndexError("Candidato MMR ausente no índice denso.")
        normalized = np.asarray(vector, dtype=np.float32).reshape(-1)
        if not normalized.size or not np.all(np.isfinite(normalized)):
            raise DenseIndexError("Vetor inválido na seleção MMR.")
        norm = float(np.linalg.norm(normalized))
        if norm == 0:
            raise DenseIndexError("Vetor nulo na seleção MMR.")
        vectors.append(normalized / norm)
        if item.retrieval_score is None or not math.isfinite(item.retrieval_score):
            raise DenseIndexError("Candidato MMR sem score denso válido.")
        relevance.append(float(item.retrieval_score))

    matrix = np.asarray(vectors, dtype=np.float32)
    similarities = matrix @ matrix.T
    selected: list[int] = []
    remaining = set(range(len(values)))
    while remaining and len(selected) < min(top_k, len(values)):
        def score(index: int) -> tuple[float, int]:
            redundancy = max((float(similarities[index, prior]) for prior in selected), default=0.0)
            mmr = relevance_weight * relevance[index] - (1.0 - relevance_weight) * redundancy
            return mmr, -index

        chosen = max(remaining, key=score)
        selected.append(chosen)
        remaining.remove(chosen)
    return tuple(values[index] for index in selected)
