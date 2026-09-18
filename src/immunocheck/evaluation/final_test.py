from __future__ import annotations

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
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    EndToEndItem,
    load_end_to_end_items,
)

FINAL_TEST_BOOTSTRAP_RESAMPLES = 2_000
FINAL_TEST_BOOTSTRAP_SEED = 20260918
FINAL_TEST_EXPECTED_ITEMS = 64


def load_frozen_test_items(root: Path) -> tuple[EndToEndItem, ...]:
    """Único loader autorizado da partição de teste após o gate final."""
    validate_freeze_manifest(root=root)
    items = load_end_to_end_items(root / "items.jsonl", require_reviewed=True)
    test_items = tuple(item for item in items if item.split is DatasetSplit.TEST)
    if len(test_items) != FINAL_TEST_EXPECTED_ITEMS:
        raise EndToEndDatasetError(
            f"O teste congelado deve conter {FINAL_TEST_EXPECTED_ITEMS} itens."
        )
    return test_items


def validate_final_test_checkpoint(
    records: Sequence[Mapping[str, object]], items: Sequence[EndToEndItem]
) -> None:
    if len(items) != FINAL_TEST_EXPECTED_ITEMS or any(
        item.split is not DatasetSplit.TEST for item in items
    ):
        raise EndToEndDatasetError("O executor final aceita somente o teste congelado completo.")
    if len(records) > len(items):
        raise EndToEndDatasetError("Checkpoint possui mais registros que o teste.")
    for expected, record in zip(items, records, strict=False):
        if record.get("item_id") != expected.item_id:
            raise EndToEndDatasetError("Checkpoint não é prefixo ordenado do teste.")
        if record.get("claim_family") != expected.claim_family:
            raise EndToEndDatasetError("Família do checkpoint diverge do teste.")
        if record.get("expected_label") != expected.label.value:
            raise EndToEndDatasetError("Rótulo do checkpoint diverge do teste congelado.")
        _validate_result(record.get("result"))


def summarize_final_test(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
    *,
    bootstrap_resamples: int = FINAL_TEST_BOOTSTRAP_RESAMPLES,
    seed: int = FINAL_TEST_BOOTSTRAP_SEED,
) -> dict[str, object]:
    validate_final_test_checkpoint(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("O resumo final exige os 64 itens de teste.")
    if bootstrap_resamples <= 0:
        raise ValueError("Bootstrap exige pelo menos uma reamostragem.")

    expected = [str(record["expected_label"]) for record in records]
    predicted = [str(_result(record)["verdict"]) for record in records]
    families = [str(record["claim_family"]) for record in records]
    results = [_result(record) for record in records]
    item_by_id = {item.item_id: item for item in items}
    ordered_items = [item_by_id[str(record["item_id"])] for record in records]
    return {
        "item_count": len(records),
        "family_count": len(set(families)),
        "metrics": _metrics(expected, predicted, results, ordered_items),
        "bootstrap": _family_bootstrap(
            expected,
            predicted,
            families,
            resamples=bootstrap_resamples,
            seed=seed,
        ),
    }


def _metrics(
    expected: Sequence[str],
    predicted: Sequence[str],
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
) -> dict[str, object]:
    labels = [item.value for item in Verdict]
    precision, recall, per_class_f1, support = precision_recall_fscore_support(
        expected, predicted, labels=labels, zero_division=0
    )
    insufficient = Verdict.INSUFFICIENT_EVIDENCE.value
    expected_abstention = [label == insufficient for label in expected]
    predicted_abstention = [label == insufficient for label in predicted]
    abstention_precision, abstention_recall, abstention_f1, _ = precision_recall_fscore_support(
        expected_abstention,
        predicted_abstention,
        average="binary",
        zero_division=0,
    )
    conclusive = [index for index, label in enumerate(expected) if label != insufficient]
    citation_hits = sum(
        bool(set(items[index].evidence_chunk_ids) & set(records[index]["source_ids"]))
        for index in conclusive
    )
    invoked = [record for record in records if record.get("auditor_invoked") is True]
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(expected, predicted, average="weighted", zero_division=0)),
        "per_class": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(per_class_f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(labels)
        },
        "confusion_matrix_reference_rows": confusion_matrix(
            expected, predicted, labels=labels
        ).tolist(),
        "abstention": {
            "precision": float(abstention_precision),
            "recall": float(abstention_recall),
            "f1": float(abstention_f1),
        },
        "relevant_citation_hit_rate_on_conclusive_items": citation_hits / len(conclusive),
        "technical_failure_rate": sum(
            record.get("technical_error") is not None for record in records
        )
        / len(records),
        "auditor_invocation_rate": len(invoked) / len(records),
        "auditor_approval_rate_when_invoked": (
            sum(record.get("auditor_approved") is True for record in invoked) / len(invoked)
            if invoked
            else None
        ),
        "latency_ms": _latency_summary([float(record["latency_ms"]) for record in records]),
    }


def _family_bootstrap(
    expected: Sequence[str],
    predicted: Sequence[str],
    families: Sequence[str],
    *,
    resamples: int,
    seed: int,
) -> dict[str, object]:
    indices_by_family: dict[str, list[int]] = defaultdict(list)
    for index, family in enumerate(families):
        indices_by_family[family].append(index)
    unique_families = sorted(indices_by_family)
    rng = random.Random(seed)
    samples: dict[str, list[float]] = defaultdict(list)
    insufficient = Verdict.INSUFFICIENT_EVIDENCE.value
    misleading = Verdict.MISLEADING.value
    labels = [item.value for item in Verdict]
    for _ in range(resamples):
        sampled_families = rng.choices(unique_families, k=len(unique_families))
        indices = [index for family in sampled_families for index in indices_by_family[family]]
        y_true = [expected[index] for index in indices]
        y_pred = [predicted[index] for index in indices]
        samples["macro_f1"].append(
            float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
        )
        samples["balanced_accuracy"].append(float(balanced_accuracy_score(y_true, y_pred)))
        samples["accuracy"].append(float(accuracy_score(y_true, y_pred)))
        samples["abstention_recall"].append(_binary_recall(y_true, y_pred, positive=insufficient))
        samples["misleading_recall"].append(_binary_recall(y_true, y_pred, positive=misleading))
    return {
        "unit": "claim_family",
        "resamples": resamples,
        "seed": seed,
        "95_percentile_interval": {
            name: _percentile_interval(values) for name, values in samples.items()
        },
    }


def _binary_recall(expected: Sequence[str], predicted: Sequence[str], *, positive: str) -> float:
    positives = [index for index, label in enumerate(expected) if label == positive]
    if not positives:
        return 0.0
    return sum(predicted[index] == positive for index in positives) / len(positives)


def _validate_result(value: object) -> None:
    if not isinstance(value, dict):
        raise EndToEndDatasetError("Registro final sem resultado.")
    try:
        Verdict(value["verdict"])
        float(value["latency_ms"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError("Resultado final inválido.") from exc
    source_ids = value.get("source_ids")
    if not isinstance(source_ids, list) or any(not isinstance(item, str) for item in source_ids):
        raise EndToEndDatasetError("Citações inválidas no resultado final.")


def _result(record: Mapping[str, object]) -> Mapping[str, object]:
    value = record.get("result")
    _validate_result(value)
    assert isinstance(value, dict)
    return value


def _latency_summary(values: Sequence[float]) -> dict[str, float | int]:
    return {
        "median": statistics.median(values),
        "p95": sorted(values)[math.ceil(0.95 * len(values)) - 1],
        "samples": len(values),
    }


def _percentile_interval(values: Sequence[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "lower": _percentile(ordered, 0.025),
        "median": _percentile(ordered, 0.5),
        "upper": _percentile(ordered, 0.975),
    }


def _percentile(ordered: Sequence[float], quantile: float) -> float:
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)
