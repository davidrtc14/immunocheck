from __future__ import annotations

import numpy as np
import pytest

from immunocheck.domain.models import Evidence
from immunocheck.retrieval.dense import DenseIndexError
from immunocheck.retrieval.mmr import maximal_marginal_relevance


def _evidence(chunk_id: str, score: float) -> Evidence:
    return Evidence(
        chunk_id=chunk_id,
        text=chunk_id,
        source_name="Fonte",
        document_title="Documento",
        url="https://example.org",
        retrieval_score=score,
    )


def test_mmr_preserves_relevance_then_selects_non_redundant_candidate() -> None:
    candidates = (
        _evidence("a", 1.0),
        _evidence("a-neighbor", 0.99),
        _evidence("b", 0.8),
    )
    vectors = {
        "a": np.asarray([1.0, 0.0], dtype=np.float32),
        "a-neighbor": np.asarray([0.999, 0.001], dtype=np.float32),
        "b": np.asarray([0.0, 1.0], dtype=np.float32),
    }

    result = maximal_marginal_relevance(
        candidates,
        vectors,
        top_k=2,
        relevance_weight=0.7,
    )

    assert [item.chunk_id for item in result] == ["a", "b"]


def test_mmr_is_deterministic_on_ties_and_caps_output() -> None:
    candidates = (_evidence("a", 0.5), _evidence("b", 0.5))
    vectors = {
        "a": np.asarray([1.0, 0.0], dtype=np.float32),
        "b": np.asarray([0.0, 1.0], dtype=np.float32),
    }

    result = maximal_marginal_relevance(candidates, vectors, top_k=3)

    assert [item.chunk_id for item in result] == ["a", "b"]


def test_mmr_rejects_missing_vector_or_invalid_parameters() -> None:
    candidates = (_evidence("a", 0.5),)
    with pytest.raises(DenseIndexError, match="ausente"):
        maximal_marginal_relevance(candidates, {}, top_k=1)
    with pytest.raises(ValueError, match="top_k"):
        maximal_marginal_relevance(candidates, {}, top_k=0)
    with pytest.raises(ValueError, match="relevance_weight"):
        maximal_marginal_relevance(candidates, {}, top_k=1, relevance_weight=1.1)
