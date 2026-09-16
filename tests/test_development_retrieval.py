from __future__ import annotations

from dataclasses import replace

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.development_retrieval import (
    build_development_retrieval_judgments,
    cluster_bootstrap_retrieval,
)
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError
from tests.test_lexical_baseline import fixture_items


def test_builds_only_conclusive_development_judgments() -> None:
    judgments, families = build_development_retrieval_judgments(fixture_items())
    assert len(judgments) == 24
    assert len(families) == 24
    assert all(judgment.relevant_chunk_ids == ("fixture",) for judgment in judgments)
    assert all(
        judgment.query_id.endswith(
            (Verdict.SUPPORTED.value, Verdict.REFUTED.value, Verdict.MISLEADING.value)
        )
        for judgment in judgments
    )


def test_rejects_test_contamination() -> None:
    items = fixture_items()
    with pytest.raises(EndToEndDatasetError, match="somente desenvolvimento"):
        build_development_retrieval_judgments(
            (replace(items[0], split=DatasetSplit.TEST), *items[1:])
        )


def test_cluster_bootstrap_is_deterministic_and_paired() -> None:
    judgments, families = build_development_retrieval_judgments(fixture_items())
    perfect = {judgment.query_id: ("fixture", "other") for judgment in judgments}
    delayed = {judgment.query_id: ("other", "fixture") for judgment in judgments}
    rankings = {
        "bm25": delayed,
        "dense_bge_m3": delayed,
        "hybrid_rrf": perfect,
        "hybrid_rrf_reranked": perfect,
    }
    first = cluster_bootstrap_retrieval(judgments, rankings, families, resamples=50, seed=7)
    second = cluster_bootstrap_retrieval(judgments, rankings, families, resamples=50, seed=7)
    assert first == second
    delta = first["paired_deltas_95_percentile_interval"]["hybrid_rrf_minus_bm25"]
    assert delta["reciprocal_rank"] == {"lower": 0.5, "median": 0.5, "upper": 0.5}
    reranker_delta = first["paired_deltas_95_percentile_interval"][
        "hybrid_rrf_reranked_minus_hybrid_rrf"
    ]
    assert reranker_delta["ndcg_at_10"] == {"lower": 0.0, "median": 0.0, "upper": 0.0}
