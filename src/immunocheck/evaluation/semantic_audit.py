"""Triagem semântica pré-congelamento; similaridade não decide vazamento sozinha."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError, EndToEndItem


@dataclass(frozen=True, slots=True)
class SemanticPair:
    development_item_id: str
    test_item_id: str
    development_family: str
    test_family: str
    cosine_similarity: float
    development_claim: str
    test_claim: str


def rank_cross_split_semantic_pairs(
    items: tuple[EndToEndItem, ...],
    embeddings: NDArray[np.float32],
    *,
    limit: int = 40,
) -> tuple[SemanticPair, ...]:
    """Ranqueia candidatos; todo resultado requer interpretação humana."""
    if limit <= 0:
        raise ValueError("limit deve ser positivo.")
    matrix = np.asarray(embeddings, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[0] != len(items) or matrix.shape[1] <= 0:
        raise EndToEndDatasetError("Embeddings incompatíveis com o dataset.")
    if not np.all(np.isfinite(matrix)):
        raise EndToEndDatasetError("Embeddings contêm valor não finito.")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise EndToEndDatasetError("Embedding nulo na auditoria semântica.")
    normalized = matrix / norms
    development = [
        index for index, item in enumerate(items) if item.split is DatasetSplit.DEVELOPMENT
    ]
    test = [index for index, item in enumerate(items) if item.split is DatasetSplit.TEST]
    if not development or not test:
        raise EndToEndDatasetError("A auditoria exige os dois splits.")
    pairs: list[SemanticPair] = []
    for dev_index in development:
        dev = items[dev_index]
        for test_index in test:
            other = items[test_index]
            if dev.claim_family == other.claim_family:
                raise EndToEndDatasetError("Uma família aparece nos dois splits.")
            pairs.append(
                SemanticPair(
                    development_item_id=dev.item_id,
                    test_item_id=other.item_id,
                    development_family=dev.claim_family or "",
                    test_family=other.claim_family or "",
                    cosine_similarity=float(normalized[dev_index] @ normalized[test_index]),
                    development_claim=dev.claim,
                    test_claim=other.claim,
                )
            )
    return tuple(
        sorted(
            pairs,
            key=lambda pair: (
                -pair.cosine_similarity,
                pair.development_item_id,
                pair.test_item_id,
            ),
        )[:limit]
    )
