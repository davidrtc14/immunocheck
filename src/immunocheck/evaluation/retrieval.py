from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

RETRIEVAL_JUDGMENT_SCHEMA_VERSION = 1
RETRIEVAL_RANKING_DEPTH = 10
RRF_INPUT_DEPTH = 60
RRF_RANK_CONSTANT = 60
ANNOTATION_CANDIDATE_DEPTH = 20


class RetrievalEvaluationError(RuntimeError):
    """Indica que julgamentos ou rankings não permitem uma avaliação válida."""


class AnnotationStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"


@dataclass(frozen=True, slots=True)
class RetrievalJudgment:
    query_id: str
    query: str
    status: AnnotationStatus
    relevant_chunk_ids: tuple[str, ...]
    notes: str | None = None
    reviewer: str | None = None
    reviewed_at: str | None = None


@dataclass(frozen=True, slots=True)
class QueryRetrievalMetrics:
    query_id: str
    recall_at_5: float
    recall_at_10: float
    reciprocal_rank: float
    ndcg_at_10: float


@dataclass(frozen=True, slots=True)
class AggregateRetrievalMetrics:
    query_count: int
    recall_at_5: float
    recall_at_10: float
    mrr: float
    ndcg_at_10: float
    per_query: tuple[QueryRetrievalMetrics, ...]


def load_retrieval_judgments(
    path: Path,
    *,
    valid_chunk_ids: AbstractSet[str] | None = None,
    require_reviewed: bool = False,
) -> tuple[RetrievalJudgment, ...]:
    if not path.is_file():
        raise RetrievalEvaluationError(f"Arquivo de julgamentos ausente: {path}")

    judgments: list[RetrievalJudgment] = []
    try:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                value = json.loads(line)
                judgments.append(_parse_judgment(value, line_number))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise RetrievalEvaluationError("O arquivo de julgamentos está inválido.") from exc

    if not judgments:
        raise RetrievalEvaluationError("O arquivo não contém consultas de avaliação.")
    query_ids = [item.query_id for item in judgments]
    if len(set(query_ids)) != len(query_ids):
        raise RetrievalEvaluationError("O arquivo contém query_id duplicado.")

    if require_reviewed:
        drafts = [
            item.query_id for item in judgments if item.status is not AnnotationStatus.REVIEWED
        ]
        if drafts:
            raise RetrievalEvaluationError(
                "Existem consultas sem revisão humana: " + ", ".join(drafts)
            )

    if valid_chunk_ids is not None:
        unknown = sorted(
            chunk_id
            for item in judgments
            for chunk_id in item.relevant_chunk_ids
            if chunk_id not in valid_chunk_ids
        )
        if unknown:
            raise RetrievalEvaluationError(
                "Os julgamentos referenciam chunks ausentes do corpus: " + ", ".join(unknown)
            )
    return tuple(judgments)


def evaluate_rankings(
    judgments: Sequence[RetrievalJudgment],
    rankings: Mapping[str, Sequence[str]],
) -> AggregateRetrievalMetrics:
    if not judgments:
        raise RetrievalEvaluationError("A avaliação exige pelo menos um julgamento.")

    per_query: list[QueryRetrievalMetrics] = []
    for judgment in judgments:
        if judgment.status is not AnnotationStatus.REVIEWED:
            raise RetrievalEvaluationError(
                f"A consulta {judgment.query_id} ainda não teve revisão humana."
            )
        if not judgment.relevant_chunk_ids:
            raise RetrievalEvaluationError(
                f"A consulta {judgment.query_id} não possui chunk relevante anotado."
            )
        if judgment.query_id not in rankings:
            raise RetrievalEvaluationError(f"Ranking ausente para {judgment.query_id}.")

        ranking = _deduplicate(rankings[judgment.query_id])
        relevant = set(judgment.relevant_chunk_ids)
        per_query.append(
            QueryRetrievalMetrics(
                query_id=judgment.query_id,
                recall_at_5=recall_at_k(ranking, relevant, k=5),
                recall_at_10=recall_at_k(ranking, relevant, k=10),
                reciprocal_rank=reciprocal_rank(ranking, relevant),
                ndcg_at_10=ndcg_at_k(ranking, relevant, k=10),
            )
        )

    count = len(per_query)
    return AggregateRetrievalMetrics(
        query_count=count,
        recall_at_5=sum(item.recall_at_5 for item in per_query) / count,
        recall_at_10=sum(item.recall_at_10 for item in per_query) / count,
        mrr=sum(item.reciprocal_rank for item in per_query) / count,
        ndcg_at_10=sum(item.ndcg_at_10 for item in per_query) / count,
        per_query=tuple(per_query),
    )


def recall_at_k(ranking: Sequence[str], relevant: AbstractSet[str], *, k: int) -> float:
    _validate_metric_inputs(relevant, k)
    retrieved = set(_deduplicate(ranking)[:k])
    return len(retrieved.intersection(relevant)) / len(relevant)


def reciprocal_rank(ranking: Sequence[str], relevant: AbstractSet[str]) -> float:
    if not relevant:
        raise ValueError("A métrica exige pelo menos um item relevante.")
    for rank, chunk_id in enumerate(_deduplicate(ranking), start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranking: Sequence[str], relevant: AbstractSet[str], *, k: int) -> float:
    _validate_metric_inputs(relevant, k)
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(_deduplicate(ranking)[:k], start=1)
        if chunk_id in relevant
    )
    ideal_hits = min(len(relevant), k)
    ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / ideal_dcg


def _parse_judgment(value: object, line_number: int) -> RetrievalJudgment:
    if not isinstance(value, dict):
        raise TypeError(f"A linha {line_number} deve conter um objeto JSON.")
    if value.get("schema_version") != RETRIEVAL_JUDGMENT_SCHEMA_VERSION:
        raise ValueError(f"Versão de schema inválida na linha {line_number}.")

    query_id = _required_text(value, "query_id", line_number)
    query = _required_text(value, "query", line_number)
    status = AnnotationStatus(_required_text(value, "status", line_number))
    raw_relevant = value.get("relevant_chunk_ids")
    if not isinstance(raw_relevant, list) or any(
        not isinstance(chunk_id, str) or not chunk_id.strip() for chunk_id in raw_relevant
    ):
        raise ValueError(f"relevant_chunk_ids inválido na linha {line_number}.")
    relevant_chunk_ids = tuple(raw_relevant)
    if len(set(relevant_chunk_ids)) != len(relevant_chunk_ids):
        raise ValueError(f"Chunk relevante duplicado na linha {line_number}.")
    if status is AnnotationStatus.REVIEWED and not relevant_chunk_ids:
        raise ValueError(f"Revisão sem chunk relevante na linha {line_number}.")

    notes = _optional_text(value, "notes", line_number)
    reviewer = _optional_text(value, "reviewer", line_number)
    reviewed_at = _optional_text(value, "reviewed_at", line_number)
    if status is AnnotationStatus.DRAFT and (reviewer is not None or reviewed_at is not None):
        raise ValueError(f"Rascunho não pode declarar revisão na linha {line_number}.")
    if status is AnnotationStatus.REVIEWED and (reviewer is None or reviewed_at is None):
        raise ValueError(f"Revisão sem responsável ou data na linha {line_number}.")
    return RetrievalJudgment(
        query_id=query_id,
        query=query,
        status=status,
        relevant_chunk_ids=relevant_chunk_ids,
        notes=notes,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )


def _required_text(value: dict[str, object], field: str, line_number: int) -> str:
    text = value.get(field)
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    return text.strip()


def _optional_text(value: dict[str, object], field: str, line_number: int) -> str | None:
    text = value.get(field)
    if text is None:
        return None
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    return text.strip()


def _validate_metric_inputs(relevant: AbstractSet[str], k: int) -> None:
    if k <= 0:
        raise ValueError("k deve ser positivo.")
    if not relevant:
        raise ValueError("A métrica exige pelo menos um item relevante.")


def _deduplicate(ranking: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(ranking))
