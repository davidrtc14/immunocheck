from __future__ import annotations

import pytest

from immunocheck.evaluation.ablation import (
    AblationCondition,
    render_ablation_table,
    run_ablation,
)
from immunocheck.evaluation.retrieval import (
    AnnotationStatus,
    RetrievalJudgment,
    chunk_hit_at_k,
    document_hit_at_k,
    document_id_of,
    document_recall_at_k,
    evidence_coverage_at_k,
    query_document_metrics,
)


def chunk(document: str, number: int) -> str:
    return f"{document}:p1:c{number}:hash{number}"


def test_document_id_supports_colons_and_rejects_bad_format() -> None:
    assert document_id_of("a:b:p3:c2:abc123") == "a:b"
    with pytest.raises(ValueError):
        document_id_of("sem-formato")


def test_document_metrics_credit_same_document_when_chunk_differs() -> None:
    relevant = {chunk("d1", 1), chunk("d2", 4)}
    ranking = [chunk("x", 1), chunk("d1", 7), chunk("d2", 9)]

    assert chunk_hit_at_k(ranking, relevant, k=3) == 0.0
    assert evidence_coverage_at_k(ranking, relevant, k=3) == 0.0
    assert document_hit_at_k(ranking, relevant, k=2) == 1.0
    assert document_recall_at_k(ranking, relevant, k=2) == 0.5
    assert document_recall_at_k(ranking, relevant, k=3) == 1.0
    assert document_recall_at_k(ranking, relevant, k=1) == 0.0


def test_query_document_metrics_exposes_named_depths() -> None:
    metrics = query_document_metrics([chunk("d1", 1)], {chunk("d1", 1)})
    assert metrics["mrr"] == 1.0
    assert metrics["doc_recall@15"] == 1.0
    assert {"chunk_hit@5", "doc_hit@10", "ndcg@10"} <= set(metrics)


def _judgments(count: int) -> tuple[list[RetrievalJudgment], dict[str, str]]:
    judgments = [
        RetrievalJudgment(
            query_id=f"q{i}",
            query="x",
            status=AnnotationStatus.REVIEWED,
            relevant_chunk_ids=(chunk(f"doc{i}", 1),),
            reviewer="r",
            reviewed_at="2026-10-13",
        )
        for i in range(count)
    ]
    return judgments, {f"q{i}": f"fam{i % 6}" for i in range(count)}


def test_ablation_detects_clear_gain_and_ignores_identical_system() -> None:
    judgments, families = _judgments(24)
    base = {j.query_id: [chunk("noise", 1)] for j in judgments}
    better = {j.query_id: list(j.relevant_chunk_ids) for j in judgments}
    result = run_ablation(
        judgments,
        families,
        [
            AblationCondition("base", base),
            AblationCondition("better", better),
            AblationCondition("same", dict(base)),
        ],
        baseline="base",
        resamples=200,
    )

    gain = result["paired_deltas_vs_baseline"]["better"]["doc_recall@15"]  # type: ignore[index]
    assert gain["delta"] == 1.0 and gain["favorable"] is True
    same = result["paired_deltas_vs_baseline"]["same"]["ndcg@10"]  # type: ignore[index]
    assert same["delta"] == 0.0 and not same["favorable"] and not same["unfavorable"]
    assert result["family_count"] == 6
    table = render_ablation_table(result)
    assert "| better |" in table and "▲" in table


def test_ablation_is_reproducible_and_validates_inputs() -> None:
    judgments, families = _judgments(12)
    rankings = {j.query_id: list(j.relevant_chunk_ids) for j in judgments}
    conditions = [AblationCondition("a", rankings), AblationCondition("b", rankings)]
    first = run_ablation(judgments, families, conditions, baseline="a", resamples=50)
    second = run_ablation(judgments, families, conditions, baseline="a", resamples=50)
    assert first == second
    with pytest.raises(ValueError):
        run_ablation(judgments, families, conditions, baseline="ausente")
    with pytest.raises(ValueError):
        run_ablation(judgments, {"q0": "f"}, conditions, baseline="a")
