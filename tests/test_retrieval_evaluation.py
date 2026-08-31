from __future__ import annotations

import json
from pathlib import Path

import pytest

from immunocheck.evaluation.retrieval import (
    AnnotationStatus,
    RetrievalEvaluationError,
    RetrievalJudgment,
    evaluate_rankings,
    load_retrieval_judgments,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
)


def reviewed(query_id: str, relevant: tuple[str, ...]) -> RetrievalJudgment:
    return RetrievalJudgment(
        query_id=query_id,
        query="alegação",
        status=AnnotationStatus.REVIEWED,
        relevant_chunk_ids=relevant,
        reviewer="anotador",
        reviewed_at="2026-08-31",
    )


def test_binary_retrieval_metrics() -> None:
    ranking = ("noise", "relevant-a", "noise-2", "relevant-b")
    relevant = {"relevant-a", "relevant-b"}

    assert recall_at_k(ranking, relevant, k=2) == 0.5
    assert recall_at_k(ranking, relevant, k=10) == 1.0
    assert reciprocal_rank(ranking, relevant) == 0.5
    assert ndcg_at_k(ranking, relevant, k=10) == pytest.approx(0.6509209)


def test_duplicate_ranking_item_does_not_improve_metrics() -> None:
    ranking = ("noise", "noise", "relevant")

    assert reciprocal_rank(ranking, {"relevant"}) == 0.5


def test_evaluate_rankings_uses_macro_average() -> None:
    judgments = (reviewed("q1", ("a",)), reviewed("q2", ("b",)))
    rankings = {"q1": ("a",), "q2": ("x", "b")}

    result = evaluate_rankings(judgments, rankings)

    assert result.query_count == 2
    assert result.recall_at_5 == 1.0
    assert result.mrr == 0.75


def test_draft_is_rejected_by_evaluation() -> None:
    draft = RetrievalJudgment("q1", "alegação", AnnotationStatus.DRAFT, ())

    with pytest.raises(RetrievalEvaluationError, match="revisão humana"):
        evaluate_rankings((draft,), {"q1": ("chunk",)})


def test_loader_validates_schema_review_and_corpus_ids(tmp_path: Path) -> None:
    path = tmp_path / "judgments.jsonl"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "query_id": "q1",
                "query": "alegação",
                "status": "reviewed",
                "relevant_chunk_ids": ["chunk-a"],
                "notes": None,
                "reviewer": "anotador",
                "reviewed_at": "2026-08-31",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = load_retrieval_judgments(
        path,
        valid_chunk_ids={"chunk-a"},
        require_reviewed=True,
    )
    assert result[0].relevant_chunk_ids == ("chunk-a",)

    with pytest.raises(RetrievalEvaluationError, match="ausentes do corpus"):
        load_retrieval_judgments(path, valid_chunk_ids={"other"})


def test_loader_refuses_draft_when_review_is_required(tmp_path: Path) -> None:
    path = tmp_path / "draft.jsonl"
    path.write_text(
        '{"schema_version":1,"query_id":"q1","query":"alegação",'
        '"status":"draft","relevant_chunk_ids":[],"notes":null,'
        '"reviewer":null,"reviewed_at":null}\n',
        encoding="utf-8",
    )

    with pytest.raises(RetrievalEvaluationError, match="sem revisão humana"):
        load_retrieval_judgments(path, require_reviewed=True)


@pytest.mark.parametrize("k", (0, -1))
def test_metrics_require_positive_k(k: int) -> None:
    with pytest.raises(ValueError, match="positivo"):
        recall_at_k(("a",), {"a"}, k=k)
