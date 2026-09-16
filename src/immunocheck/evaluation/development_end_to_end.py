from __future__ import annotations

import hashlib
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
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    EndToEndItem,
)

END_TO_END_CONDITIONS = (
    "bm25_no_auditor",
    "dense_no_auditor",
    "dense_with_auditor",
    "hybrid_reranked_with_auditor",
)
END_TO_END_BOOTSTRAP_RESAMPLES = 2_000
END_TO_END_BOOTSTRAP_SEED = 20260916


def load_checkpoint(path: Path) -> tuple[dict[str, object], ...]:
    if not path.exists():
        return ()
    records: list[dict[str, object]] = []
    try:
        with path.open(encoding="utf-8") as source:
            for line in source:
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError
                    records.append(value)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise EndToEndDatasetError("Checkpoint fim a fim inválido.") from exc
    return tuple(records)


def validate_checkpoint_prefix(
    records: Sequence[Mapping[str, object]], items: Sequence[EndToEndItem]
) -> None:
    if any(item.split is not DatasetSplit.DEVELOPMENT for item in items):
        raise EndToEndDatasetError("O experimento fim a fim aceita somente desenvolvimento.")
    if len(records) > len(items):
        raise EndToEndDatasetError("Checkpoint possui mais registros que o desenvolvimento.")
    for expected, record in zip(items, records, strict=False):
        if record.get("item_id") != expected.item_id:
            raise EndToEndDatasetError("Checkpoint não é prefixo ordenado do desenvolvimento.")
        if record.get("claim_family") != expected.claim_family:
            raise EndToEndDatasetError("Família do checkpoint diverge do benchmark.")
        if record.get("expected_label") != expected.label.value:
            raise EndToEndDatasetError("Rótulo do checkpoint diverge do benchmark.")
        conditions = record.get("conditions")
        if not isinstance(conditions, dict) or tuple(conditions) != END_TO_END_CONDITIONS:
            raise EndToEndDatasetError("Condições do checkpoint estão incompletas ou reordenadas.")


def summarize_end_to_end_records(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
    *,
    bootstrap_resamples: int = END_TO_END_BOOTSTRAP_RESAMPLES,
    seed: int = END_TO_END_BOOTSTRAP_SEED,
) -> dict[str, object]:
    validate_checkpoint_prefix(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("O resumo exige todos os itens de desenvolvimento.")
    if bootstrap_resamples <= 0:
        raise ValueError("Bootstrap exige pelo menos uma reamostragem.")

    expected = [str(record["expected_label"]) for record in records]
    families = [str(record["claim_family"]) for record in records]
    item_by_id = {item.item_id: item for item in items}
    systems: dict[str, dict[str, object]] = {}
    predictions: dict[str, list[str]] = {}
    for condition in END_TO_END_CONDITIONS:
        condition_records = [_condition_record(record, condition) for record in records]
        predicted = [str(record["verdict"]) for record in condition_records]
        predictions[condition] = predicted
        systems[condition] = _condition_metrics(
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
    extraction_records = [record.get("extraction") for record in records]
    if any(not isinstance(record, dict) for record in extraction_records):
        raise EndToEndDatasetError("Registros de extração ausentes.")
    typed_extraction = [record for record in extraction_records if isinstance(record, dict)]
    return {
        "item_count": len(records),
        "family_count": len(set(families)),
        "systems": systems,
        "extraction": {
            "in_scope_rate": sum(record.get("claim") is not None for record in typed_extraction)
            / len(records),
            "technical_failure_rate": sum(
                record.get("technical_error") is not None for record in typed_extraction
            )
            / len(records),
            "latency_ms": _latency_summary(
                [float(record["latency_ms"]) for record in typed_extraction]
            ),
        },
        "bootstrap": bootstrap,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _condition_record(record: Mapping[str, object], condition: str) -> Mapping[str, object]:
    conditions = record.get("conditions")
    if not isinstance(conditions, dict):
        raise EndToEndDatasetError("Registro sem condições fim a fim.")
    value = conditions.get(condition)
    if not isinstance(value, dict):
        raise EndToEndDatasetError(f"Registro sem a condição {condition}.")
    try:
        Verdict(value["verdict"])
        float(value["latency_ms"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError(f"Saída inválida na condição {condition}.") from exc
    source_ids = value.get("source_ids")
    if not isinstance(source_ids, list) or any(not isinstance(item, str) for item in source_ids):
        raise EndToEndDatasetError(f"Citações inválidas na condição {condition}.")
    return value


def _condition_metrics(
    expected: Sequence[str],
    predicted: Sequence[str],
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
) -> dict[str, object]:
    label_order = [item.value for item in Verdict]
    precision, recall, per_class_f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=label_order,
        zero_division=0,
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
    conclusive_indices = [index for index, label in enumerate(expected) if label != insufficient]
    citation_hits = 0
    for index in conclusive_indices:
        annotated = set(items[index].evidence_chunk_ids)
        displayed = set(records[index]["source_ids"])
        citation_hits += bool(annotated & displayed)
    invoked = [record for record in records if record.get("auditor_invoked") is True]
    latencies = [float(record["latency_ms"]) for record in records]
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
            for index, label in enumerate(label_order)
        },
        "confusion_matrix_reference_rows": confusion_matrix(
            expected, predicted, labels=label_order
        ).tolist(),
        "abstention": {
            "precision": float(abstention_precision),
            "recall": float(abstention_recall),
            "f1": float(abstention_f1),
        },
        "relevant_citation_hit_rate_on_conclusive_items": citation_hits / len(conclusive_indices),
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
        "latency_ms": _latency_summary(latencies),
    }


def _family_bootstrap(
    expected: Sequence[str],
    predictions: Mapping[str, Sequence[str]],
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
    samples = {condition: [] for condition in END_TO_END_CONDITIONS}
    for _ in range(resamples):
        sampled_families = rng.choices(unique_families, k=len(unique_families))
        sampled_indices = [
            index for family in sampled_families for index in indices_by_family[family]
        ]
        sampled_expected = [expected[index] for index in sampled_indices]
        for condition in END_TO_END_CONDITIONS:
            sampled_predictions = [predictions[condition][index] for index in sampled_indices]
            samples[condition].append(
                float(
                    f1_score(
                        sampled_expected,
                        sampled_predictions,
                        labels=[item.value for item in Verdict],
                        average="macro",
                        zero_division=0,
                    )
                )
            )
    intervals = {condition: _percentile_interval(values) for condition, values in samples.items()}
    comparisons = {}
    for candidate, baseline in (
        ("dense_with_auditor", "dense_no_auditor"),
        ("hybrid_reranked_with_auditor", "dense_with_auditor"),
        ("hybrid_reranked_with_auditor", "dense_no_auditor"),
    ):
        comparisons[f"{candidate}_minus_{baseline}"] = _percentile_interval(
            [
                candidate_value - baseline_value
                for candidate_value, baseline_value in zip(
                    samples[candidate], samples[baseline], strict=True
                )
            ]
        )
    return {
        "unit": "claim_family",
        "resamples": resamples,
        "seed": seed,
        "macro_f1_95_percentile_interval": intervals,
        "paired_macro_f1_deltas_95_percentile_interval": comparisons,
    }


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
