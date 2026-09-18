"""Resumo reproduzível das medições operacionais multimodais."""

from __future__ import annotations

import math
import statistics
from collections.abc import Mapping, Sequence


def summarize_latency(
    values_ms: Sequence[float],
    *,
    target_ms: float,
) -> dict[str, float | int | bool]:
    """Resume latências com P95 pela regra do posto mais próximo."""

    if not values_ms:
        raise ValueError("A série de latência não pode estar vazia.")
    if target_ms <= 0:
        raise ValueError("A meta de latência deve ser positiva.")
    values = [float(value) for value in values_ms]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("Latências devem ser números finitos e não negativos.")
    ordered = sorted(values)
    p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]
    return {
        "samples": len(values),
        "minimum_ms": ordered[0],
        "median_ms": statistics.median(values),
        "mean_ms": statistics.fmean(values),
        "p95_ms": p95,
        "maximum_ms": ordered[-1],
        "standard_deviation_ms": statistics.stdev(values) if len(values) > 1 else 0.0,
        "target_ms": target_ms,
        "target_met": p95 <= target_ms,
    }


def summarize_modality(
    records: Sequence[Mapping[str, object]],
    *,
    target_ms: float,
) -> dict[str, object]:
    """Calcula latência e conclusão sem ocultar execuções com erro."""

    if not records:
        raise ValueError("A modalidade precisa ter ao menos uma execução.")
    total_latencies = [float(record["total_latency_ms"]) for record in records]
    normalization_latencies = [
        float(record["normalization_latency_ms"])
        for record in records
        if record.get("normalization_latency_ms") is not None
    ]
    successes = sum(record.get("technical_error") is None for record in records)
    result: dict[str, object] = {
        "runs": len(records),
        "successful_runs": successes,
        "technical_failures": len(records) - successes,
        "completion_rate": successes / len(records),
        "completion_target": 0.95,
        "completion_target_met": successes / len(records) >= 0.95,
        "total_latency": summarize_latency(total_latencies, target_ms=target_ms),
    }
    if normalization_latencies:
        result["normalization_latency"] = summarize_latency(
            normalization_latencies,
            target_ms=target_ms,
        )
    return result
