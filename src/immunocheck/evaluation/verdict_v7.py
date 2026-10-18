"""Métricas da Fase 20 (ADR-054) sobre registros de execução do veredito.

Cada registro tem `expected_label`, `verdict`, `latency_ms`, `failure` e `claim_family`. As regras e
os limites estão no Adendo 1 de `evaluation/refinement_v7/PROTOCOL.md`; este módulo só calcula.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence

LABELS = ("SUPPORTED", "REFUTED", "MISLEADING", "INSUFFICIENT_EVIDENCE")
SUPPORTED = "SUPPORTED"

Row = Mapping[str, object]


def macro_f1(rows: Sequence[Row]) -> float:
    scores = []
    for label in LABELS:
        tp = sum(1 for r in rows if r["verdict"] == label and r["expected_label"] == label)
        predicted = sum(1 for r in rows if r["verdict"] == label)
        expected = sum(1 for r in rows if r["expected_label"] == label)
        precision = tp / predicted if predicted else 0.0
        recall = tp / expected if expected else 0.0
        scores.append(2 * precision * recall / (precision + recall) if tp else 0.0)
    return sum(scores) / len(scores)


def recall_by_label(rows: Sequence[Row]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for label in LABELS:
        group = [r for r in rows if r["expected_label"] == label]
        result[label] = sum(r["verdict"] == label for r in group) / len(group) if group else None
    return result


def grave_error(rows: Sequence[Row]) -> float:
    """Fração dos itens não `SUPPORTED` respondidos como `SUPPORTED`."""

    group = [r for r in rows if r["expected_label"] != SUPPORTED]
    return sum(r["verdict"] == SUPPORTED for r in group) / len(group) if group else 0.0


def failure_rate(rows: Sequence[Row]) -> float:
    return sum(bool(r.get("failure")) for r in rows) / len(rows) if rows else 0.0


def p95_seconds(rows: Sequence[Row]) -> float:
    """Percentil 95 pelo método do posto mais próximo."""

    latencies = sorted(float(r["latency_ms"]) / 1000 for r in rows)  # type: ignore[arg-type]
    if not latencies:
        return 0.0
    return latencies[max(0, math.ceil(0.95 * len(latencies)) - 1)]


def summarize(rows: Sequence[Row]) -> dict[str, object]:
    return {
        "n": len(rows),
        "macro_f1": round(macro_f1(rows), 4),
        "recall": {k: None if v is None else round(v, 3) for k, v in recall_by_label(rows).items()},
        "grave_error": round(grave_error(rows), 4),
        "failure_rate": round(failure_rate(rows), 4),
        "p95_s": round(p95_seconds(rows), 1),
    }


def paired_family_bootstrap(
    candidate: Sequence[Row],
    reference: Sequence[Row],
    metric: Callable[[Sequence[Row]], float] = macro_f1,
    *,
    samples: int = 10_000,
    seed: int = 42,
) -> dict[str, float]:
    """Δ = métrica(candidata) − métrica(referência), com IC 95% reamostrando famílias."""

    reference_by_case = {r["case_id"]: r for r in reference}
    pairs = [(row, reference_by_case[row["case_id"]]) for row in candidate]
    if len(pairs) != len(reference_by_case):
        raise ValueError("As condições precisam cobrir os mesmos casos.")
    families: dict[object, list[tuple[Row, Row]]] = defaultdict(list)
    for pair in pairs:
        families[pair[0]["claim_family"]].append(pair)
    keys = sorted(families, key=str)
    rng = random.Random(seed)
    deltas = []
    for _ in range(samples):
        drawn = [pair for key in rng.choices(keys, k=len(keys)) for pair in families[key]]
        deltas.append(metric([c for c, _ in drawn]) - metric([r for _, r in drawn]))
    deltas.sort()
    return {
        "delta": metric([c for c, _ in pairs]) - metric([r for _, r in pairs]),
        "ci_low": deltas[int(0.025 * samples)],
        "ci_high": deltas[int(0.975 * samples) - 1],
    }
