from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError, EndToEndItem

REFINEMENT_CONDITIONS = ("v1_dense_with_auditor", "v2_separated_no_auditor")
REFINEMENT_BOOTSTRAP_RESAMPLES = 2_000
REFINEMENT_BOOTSTRAP_SEED = 20260926


def load_refinement_checkpoint(path: Path) -> tuple[dict[str, object], ...]:
    if not path.exists():
        return ()
    try:
        values = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]
    except (OSError, json.JSONDecodeError) as exc:
        raise EndToEndDatasetError("Checkpoint da calibração v2 inválido.") from exc
    if any(not isinstance(value, dict) for value in values):
        raise EndToEndDatasetError("Checkpoint da calibração v2 inválido.")
    return tuple(values)


def validate_refinement_checkpoint(
    records: Sequence[Mapping[str, object]], items: Sequence[EndToEndItem]
) -> None:
    if any(item.split is not DatasetSplit.DEVELOPMENT for item in items):
        raise EndToEndDatasetError("A calibração v2 aceita somente itens de desenvolvimento.")
    if len(records) > len(items):
        raise EndToEndDatasetError("Checkpoint possui mais registros que a calibração.")
    for item, record in zip(items, records, strict=False):
        if (
            record.get("item_id") != item.item_id
            or record.get("claim_family") != item.claim_family
            or record.get("expected_label") != item.label.value
        ):
            raise EndToEndDatasetError("Checkpoint não corresponde à calibração adjudicada.")
        conditions = record.get("conditions")
        if not isinstance(conditions, dict) or tuple(conditions) != REFINEMENT_CONDITIONS:
            raise EndToEndDatasetError("Condições do checkpoint estão ausentes ou reordenadas.")
        for condition in REFINEMENT_CONDITIONS:
            _condition_record(record, condition)


def summarize_refinement_records(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
    *,
    bootstrap_resamples: int = REFINEMENT_BOOTSTRAP_RESAMPLES,
    seed: int = REFINEMENT_BOOTSTRAP_SEED,
) -> dict[str, object]:
    validate_refinement_checkpoint(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("O resumo exige os 48 itens da calibração.")
    if bootstrap_resamples <= 0:
        raise ValueError("Bootstrap exige ao menos uma reamostragem.")
    expected = [str(record["expected_label"]) for record in records]
    families = [str(record["claim_family"]) for record in records]
    item_by_id = {item.item_id: item for item in items}
    systems: dict[str, dict[str, object]] = {}
    predictions: dict[str, list[str]] = {}
    for condition in REFINEMENT_CONDITIONS:
        condition_records = [_condition_record(record, condition) for record in records]
        predicted = [str(record["verdict"]) for record in condition_records]
        predictions[condition] = predicted
        systems[condition] = _metrics(
            expected,
            predicted,
            condition_records,
            [item_by_id[str(record["item_id"])] for record in records],
        )

    bootstrap = _family_bootstrap(
        expected,
        predictions,
        families,
        resamples=bootstrap_resamples,
        seed=seed,
    )
    gates = _promotion_gates(systems)
    extraction = [record.get("extraction") for record in records]
    if any(not isinstance(record, dict) for record in extraction):
        raise EndToEndDatasetError("Registro de extração ausente.")
    typed_extraction = [record for record in extraction if isinstance(record, dict)]
    return {
        "item_count": len(records),
        "family_count": len(set(families)),
        "systems": systems,
        "paired_bootstrap": bootstrap,
        "promotion_gates": gates,
        "factual_auditor_condition_eligible": all(gate["passed"] for gate in gates.values()),
        "extraction": {
            "in_scope_rate": sum(record.get("claim") is not None for record in typed_extraction)
            / len(records),
            "technical_failure_rate": sum(
                record.get("technical_error") is not None for record in typed_extraction
            )
            / len(records),
            "latency_ms": _latency([float(record["latency_ms"]) for record in typed_extraction]),
        },
    }


def _promotion_gates(systems: Mapping[str, Mapping[str, object]]) -> dict[str, dict[str, object]]:
    baseline = systems[REFINEMENT_CONDITIONS[0]]
    candidate = systems[REFINEMENT_CONDITIONS[1]]
    base_class = baseline["per_class"]
    candidate_class = candidate["per_class"]
    assert isinstance(base_class, dict) and isinstance(candidate_class, dict)
    recall_drops = {
        label.value: float(base_class[label.value]["recall"])
        - float(candidate_class[label.value]["recall"])
        for label in Verdict
    }
    values = {
        "macro_f1_delta": (float(candidate["macro_f1"]) - float(baseline["macro_f1"]), 0.08),
        "misleading_recall": (
            float(candidate_class[Verdict.MISLEADING.value]["recall"]),
            0.40,
        ),
        "abstention_precision": (float(candidate["abstention"]["precision"]), 0.45),
        "citation_hit_rate": (
            float(candidate["relevant_citation_hit_rate_on_conclusive_items"]),
            0.60,
        ),
        "maximum_class_recall_drop": (max(recall_drops.values()), 0.05),
        "technical_failure_rate": (float(candidate["technical_failure_rate"]), 0.02),
        "textual_p95_seconds": (float(candidate["latency_ms"]["p95"]) / 1000, 20.0),
    }
    result = {}
    for name, (value, threshold) in values.items():
        maximum = name in {
            "maximum_class_recall_drop",
            "technical_failure_rate",
            "textual_p95_seconds",
        }
        result[name] = {
            "value": value,
            "threshold": threshold,
            "direction": "maximum" if maximum else "minimum",
            "passed": value <= threshold if maximum else value >= threshold,
        }
    result["maximum_class_recall_drop"]["per_class"] = recall_drops
    return result


def _condition_record(record: Mapping[str, object], condition: str) -> Mapping[str, object]:
    conditions = record.get("conditions")
    if not isinstance(conditions, dict) or not isinstance(conditions.get(condition), dict):
        raise EndToEndDatasetError(f"Registro sem a condição {condition}.")
    value = conditions[condition]
    try:
        Verdict(value["verdict"])
        float(value["latency_ms"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError(f"Saída inválida na condição {condition}.") from exc
    source_ids = value.get("source_ids")
    if not isinstance(source_ids, list) or any(not isinstance(item, str) for item in source_ids):
        raise EndToEndDatasetError(f"Citações inválidas na condição {condition}.")
    return value


def _metrics(expected, predicted, records, items) -> dict[str, object]:
    labels = [item.value for item in Verdict]
    precision, recall, f1, support = precision_recall_fscore_support(
        expected, predicted, labels=labels, zero_division=0
    )
    insufficient = Verdict.INSUFFICIENT_EVIDENCE.value
    abstention = precision_recall_fscore_support(
        [label == insufficient for label in expected],
        [label == insufficient for label in predicted],
        average="binary",
        zero_division=0,
    )
    conclusive = [index for index, label in enumerate(expected) if label != insufficient]
    citation_hits = sum(
        bool(set(items[index].evidence_chunk_ids) & set(records[index]["source_ids"]))
        for index in conclusive
    )
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, average="macro", zero_division=0)),
        "per_class": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(labels)
        },
        "confusion_matrix_reference_rows": confusion_matrix(
            expected, predicted, labels=labels
        ).tolist(),
        "abstention": {
            "precision": float(abstention[0]),
            "recall": float(abstention[1]),
            "f1": float(abstention[2]),
        },
        "relevant_citation_hit_rate_on_conclusive_items": citation_hits / len(conclusive),
        "technical_failure_rate": sum(
            record.get("technical_error") is not None for record in records
        )
        / len(records),
        "latency_ms": _latency([float(record["latency_ms"]) for record in records]),
    }


def _family_bootstrap(expected, predictions, families, *, resamples, seed):
    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for index, family in enumerate(families):
        grouped[family].append(index)
    unique = sorted(grouped)
    rng = random.Random(seed)
    deltas = []
    labels = [item.value for item in Verdict]
    for _ in range(resamples):
        indices = [
            index for family in rng.choices(unique, k=len(unique)) for index in grouped[family]
        ]
        reference = [expected[index] for index in indices]
        baseline = [predictions[REFINEMENT_CONDITIONS[0]][index] for index in indices]
        candidate = [predictions[REFINEMENT_CONDITIONS[1]][index] for index in indices]
        deltas.append(
            float(
                f1_score(reference, candidate, labels=labels, average="macro", zero_division=0)
                - f1_score(reference, baseline, labels=labels, average="macro", zero_division=0)
            )
        )
    return {
        "unit": "claim_family",
        "resamples": resamples,
        "seed": seed,
        "candidate_minus_baseline_macro_f1_95_percentile_interval": _interval(deltas),
    }


def _latency(values: Sequence[float]) -> dict[str, float | int]:
    return {
        "median": statistics.median(values),
        "p95": sorted(values)[math.ceil(0.95 * len(values)) - 1],
        "samples": len(values),
    }


def _interval(values: Sequence[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "lower": _percentile(ordered, 0.025),
        "median": _percentile(ordered, 0.5),
        "upper": _percentile(ordered, 0.975),
    }


def _percentile(ordered: Sequence[float], quantile: float) -> float:
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)
