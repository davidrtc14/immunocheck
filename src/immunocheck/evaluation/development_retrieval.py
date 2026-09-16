"""Julgamentos e incerteza do retrieval usando apenas desenvolvimento."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence

import numpy as np

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError, EndToEndItem
from immunocheck.evaluation.retrieval import (
    AnnotationStatus,
    RetrievalJudgment,
    evaluate_rankings,
)

RETRIEVAL_BOOTSTRAP_RESAMPLES = 2000
RETRIEVAL_BOOTSTRAP_SEED = 20260916
RETRIEVAL_METRICS = ("recall_at_5", "recall_at_10", "reciprocal_rank", "ndcg_at_10")


def build_development_retrieval_judgments(
    items: Sequence[EndToEndItem],
) -> tuple[tuple[RetrievalJudgment, ...], dict[str, str]]:
    values = tuple(items)
    if not values or any(item.split is not DatasetSplit.DEVELOPMENT for item in values):
        raise EndToEndDatasetError("Julgamentos de retrieval aceitam somente desenvolvimento.")
    selected = tuple(item for item in values if item.label is not Verdict.INSUFFICIENT_EVIDENCE)
    if any(not item.evidence_chunk_ids for item in selected):
        raise EndToEndDatasetError("Item conclusivo sem evidência para retrieval.")
    judgments = tuple(
        RetrievalJudgment(
            query_id=item.item_id,
            query=item.claim,
            status=AnnotationStatus.REVIEWED,
            relevant_chunk_ids=item.evidence_chunk_ids,
            notes="Derivado do benchmark congelado; split development.",
            reviewer=item.adjudicator or item.second_reviewer or item.reviewer,
            reviewed_at=item.adjudicated_at or item.second_reviewed_at or item.reviewed_at,
        )
        for item in selected
    )
    families = {item.item_id: item.claim_family or "" for item in selected}
    if any(not family for family in families.values()):
        raise EndToEndDatasetError("Julgamento sem claim_family.")
    return judgments, families


def cluster_bootstrap_retrieval(
    judgments: Sequence[RetrievalJudgment],
    rankings_by_system: Mapping[str, Mapping[str, Sequence[str]]],
    families: Mapping[str, str],
    *,
    resamples: int = RETRIEVAL_BOOTSTRAP_RESAMPLES,
    seed: int = RETRIEVAL_BOOTSTRAP_SEED,
) -> dict[str, object]:
    if resamples <= 0 or len(rankings_by_system) < 2:
        raise ValueError("Bootstrap exige reamostragens e pelo menos dois sistemas.")
    query_ids = {judgment.query_id for judgment in judgments}
    if set(families) != query_ids:
        raise ValueError("Famílias não correspondem aos julgamentos.")
    per_system: dict[str, dict[str, object]] = {}
    for name, rankings in rankings_by_system.items():
        aggregate = evaluate_rankings(judgments, rankings)
        per_system[name] = {item.query_id: item for item in aggregate.per_query}

    queries_by_family: dict[str, list[str]] = defaultdict(list)
    for query_id, family in families.items():
        queries_by_family[family].append(query_id)
    family_names = tuple(sorted(queries_by_family))
    rng = np.random.default_rng(seed)
    samples = {system: {metric: [] for metric in RETRIEVAL_METRICS} for system in per_system}
    for _ in range(resamples):
        selected_families = rng.choice(family_names, size=len(family_names), replace=True)
        selected_queries = [
            query_id for family in selected_families for query_id in queries_by_family[str(family)]
        ]
        for system, values in per_system.items():
            for metric in RETRIEVAL_METRICS:
                samples[system][metric].append(
                    float(
                        np.mean(
                            [getattr(values[query_id], metric) for query_id in selected_queries]
                        )
                    )
                )

    intervals = {
        system: {metric: _interval(values) for metric, values in metrics.items()}
        for system, metrics in samples.items()
    }
    comparisons: dict[str, dict[str, dict[str, float]]] = {}
    if "hybrid_rrf" in samples:
        for comparator in ("bm25", "dense_bge_m3"):
            if comparator not in samples:
                continue
            comparisons[f"hybrid_rrf_minus_{comparator}"] = {
                metric: _interval(
                    [
                        hybrid - baseline
                        for hybrid, baseline in zip(
                            samples["hybrid_rrf"][metric],
                            samples[comparator][metric],
                            strict=True,
                        )
                    ]
                )
                for metric in RETRIEVAL_METRICS
            }
    if "hybrid_rrf_reranked" in samples:
        for comparator in ("hybrid_rrf", "dense_bge_m3"):
            if comparator not in samples:
                continue
            comparisons[f"hybrid_rrf_reranked_minus_{comparator}"] = {
                metric: _interval(
                    [
                        reranked - baseline
                        for reranked, baseline in zip(
                            samples["hybrid_rrf_reranked"][metric],
                            samples[comparator][metric],
                            strict=True,
                        )
                    ]
                )
                for metric in RETRIEVAL_METRICS
            }
    return {
        "unit": "claim_family",
        "resamples": resamples,
        "seed": seed,
        "systems_95_percentile_interval": intervals,
        "paired_deltas_95_percentile_interval": comparisons,
    }


def _interval(values: Sequence[float]) -> dict[str, float]:
    return {
        "lower": float(np.quantile(values, 0.025)),
        "median": float(np.quantile(values, 0.5)),
        "upper": float(np.quantile(values, 0.975)),
    }
