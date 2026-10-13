"""Harness de ablação de retrieval: uma tabela, mesmo conjunto, bootstrap pareado por família."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from immunocheck.evaluation.retrieval import (
    RetrievalEvaluationError,
    RetrievalJudgment,
    query_document_metrics,
)

ABLATION_BOOTSTRAP_RESAMPLES = 2000
ABLATION_BOOTSTRAP_SEED = 20261013
DEFAULT_TABLE_METRICS = ("doc_recall@15", "ndcg@10", "mrr", "chunk_hit@15")


@dataclass(frozen=True, slots=True)
class AblationCondition:
    """Uma técnica ligada ou desligada: nome e ranking (chunk_ids em ordem) por consulta."""

    name: str
    rankings: Mapping[str, Sequence[str]]


def run_ablation(
    judgments: Sequence[RetrievalJudgment],
    families: Mapping[str, str],
    conditions: Sequence[AblationCondition],
    *,
    baseline: str,
    resamples: int = ABLATION_BOOTSTRAP_RESAMPLES,
    seed: int = ABLATION_BOOTSTRAP_SEED,
) -> dict[str, object]:
    names = [condition.name for condition in conditions]
    if len(set(names)) != len(names) or baseline not in names or len(names) < 2:
        raise ValueError("A ablação exige condições únicas, incluindo a de referência.")
    if resamples <= 0:
        raise ValueError("resamples deve ser positivo.")
    query_ids = [judgment.query_id for judgment in judgments]
    if not query_ids or set(families) != set(query_ids):
        raise ValueError("Famílias devem corresponder exatamente aos julgamentos.")

    per_query: dict[str, np.ndarray] = {}
    metric_names: tuple[str, ...] = ()
    for condition in conditions:
        rows: list[list[float]] = []
        for judgment in judgments:
            if judgment.query_id not in condition.rankings:
                raise RetrievalEvaluationError(
                    f"Ranking ausente para {judgment.query_id} em {condition.name}."
                )
            metrics = query_document_metrics(
                condition.rankings[judgment.query_id], set(judgment.relevant_chunk_ids)
            )
            metric_names = tuple(metrics)
            rows.append([metrics[name] for name in metric_names])
        per_query[condition.name] = np.asarray(rows, dtype=float)

    family_names = sorted(set(families.values()))
    queries_by_family: dict[str, list[int]] = defaultdict(list)
    for index, query_id in enumerate(query_ids):
        queries_by_family[families[query_id]].append(index)
    rng = np.random.default_rng(seed)
    weights = np.zeros((resamples, len(query_ids)))
    for row in range(resamples):
        for family in rng.choice(family_names, size=len(family_names), replace=True):
            for index in queries_by_family[str(family)]:
                weights[row, index] += 1
    totals = weights.sum(axis=1, keepdims=True)
    boot = {
        name: (weights @ values) / totals for name, values in per_query.items()
    }

    systems: dict[str, dict[str, dict[str, float]]] = {}
    deltas: dict[str, dict[str, dict[str, float | bool]]] = {}
    for name, values in per_query.items():
        systems[name] = {
            metric: {"mean": float(values[:, column].mean()), **_interval(boot[name][:, column])}
            for column, metric in enumerate(metric_names)
        }
        if name == baseline:
            continue
        deltas[name] = {}
        for column, metric in enumerate(metric_names):
            difference = boot[name][:, column] - boot[baseline][:, column]
            interval = _interval(difference)
            deltas[name][metric] = {
                "delta": float(values[:, column].mean() - per_query[baseline][:, column].mean()),
                **interval,
                "favorable": bool(interval["lower"] > 0),
                "unfavorable": bool(interval["upper"] < 0),
            }
    return {
        "unit": "claim_family",
        "query_count": len(query_ids),
        "family_count": len(family_names),
        "resamples": resamples,
        "seed": seed,
        "baseline": baseline,
        "systems": systems,
        "paired_deltas_vs_baseline": deltas,
    }


def render_ablation_table(
    result: Mapping[str, object],
    *,
    metrics: Sequence[str] = DEFAULT_TABLE_METRICS,
) -> str:
    systems: Mapping[str, Mapping[str, Mapping[str, float]]] = result["systems"]  # type: ignore[assignment]
    deltas: Mapping[str, Mapping[str, Mapping[str, float]]] = result["paired_deltas_vs_baseline"]  # type: ignore[assignment]
    baseline = str(result["baseline"])
    lines = [
        f"Ablação sobre {result['query_count']} consultas e {result['family_count']} famílias "
        f"(referência: `{baseline}`; IC 95% percentil, bootstrap pareado por família).",
        "",
        "| Condição | " + " | ".join(metrics) + " |",
        "|---|" + "---|" * len(metrics),
    ]
    for name, values in systems.items():
        cells = []
        for metric in metrics:
            cell = f"{values[metric]['mean']:.3f}"
            if name != baseline:
                delta = deltas[name][metric]
                marker = " ▲" if delta["favorable"] else (" ▼" if delta["unfavorable"] else "")
                cell += f" ({delta['delta']:+.3f} [{delta['lower']:+.3f}, {delta['upper']:+.3f}]){marker}"
            cells.append(cell)
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += ["", "▲ IC do delta acima de zero; ▼ IC abaixo de zero; sem marca = inconclusivo."]
    return "\n".join(lines)


def _interval(values: np.ndarray) -> dict[str, float]:
    return {
        "lower": float(np.quantile(values, 0.025)),
        "upper": float(np.quantile(values, 0.975)),
    }
