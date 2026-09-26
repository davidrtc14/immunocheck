from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    _family_bootstrap,
    _metrics,
    _promotion_gates,
)

MINIMUM_CONFIRMATORY_ITEMS = 32
MINIMUM_ITEMS_PER_LABEL = 8
MINIMUM_NOVEL_FAMILIES = 8
CONFIRMATORY_CONDITIONS = (
    "v1_dense_with_auditor",
    "v3_routed_with_hierarchical_citations",
)


@dataclass(frozen=True, slots=True)
class ConfirmatoryDatasetSummary:
    total: int
    labels: dict[str, int]
    families: int
    topics: dict[str, int]
    evidence_chunks: int


def validate_confirmatory_checkpoint(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
) -> None:
    if len(records) > len(items):
        raise EndToEndDatasetError("Checkpoint possui mais registros que o conjunto.")
    for item, record in zip(items, records, strict=False):
        if (
            record.get("item_id") != item.item_id
            or record.get("claim_family") != item.claim_family
            or record.get("expected_label") != item.label.value
        ):
            raise EndToEndDatasetError("Checkpoint não corresponde ao conjunto confirmatório.")
        conditions = record.get("conditions")
        if not isinstance(conditions, dict) or tuple(conditions) != CONFIRMATORY_CONDITIONS:
            raise EndToEndDatasetError("Condições confirmatórias ausentes ou reordenadas.")
        for condition in CONFIRMATORY_CONDITIONS:
            value = conditions.get(condition)
            if not isinstance(value, dict):
                raise EndToEndDatasetError(f"Condição ausente: {condition}.")
            try:
                Verdict(str(value["verdict"]))
                float(value["latency_ms"])
            except (KeyError, TypeError, ValueError) as exc:
                raise EndToEndDatasetError(f"Saída inválida na condição {condition}.") from exc
            source_ids = value.get("source_ids")
            if not isinstance(source_ids, list) or any(
                not isinstance(source_id, str) for source_id in source_ids
            ):
                raise EndToEndDatasetError(f"Citações inválidas na condição {condition}.")


def summarize_confirmatory_records(
    records: Sequence[Mapping[str, object]],
    items: Sequence[EndToEndItem],
) -> dict[str, object]:
    validate_confirmatory_checkpoint(records, items)
    if len(records) != len(items):
        raise EndToEndDatasetError("O resumo exige os 32 itens confirmatórios.")

    expected = [str(record["expected_label"]) for record in records]
    families = [str(record["claim_family"]) for record in records]
    item_by_id = {item.item_id: item for item in items}
    systems: dict[str, dict[str, object]] = {}
    predictions: dict[str, list[str]] = {}
    for condition in CONFIRMATORY_CONDITIONS:
        condition_records = [record["conditions"][condition] for record in records]  # type: ignore[index]
        predicted = [str(record["verdict"]) for record in condition_records]  # type: ignore[index]
        predictions[condition] = predicted
        systems[condition] = _metrics(
            expected,
            predicted,
            condition_records,
            [item_by_id[str(record["item_id"])] for record in records],
        )

    gates = _promotion_gates(systems, conditions=CONFIRMATORY_CONDITIONS)
    candidate = systems[CONFIRMATORY_CONDITIONS[1]]
    gates = {
        "absolute_macro_f1": {
            "value": float(candidate["macro_f1"]),
            "threshold": 0.60,
            "direction": "minimum",
            "passed": float(candidate["macro_f1"]) >= 0.60,
        },
        **gates,
    }
    return {
        "item_count": len(records),
        "family_count": len(set(families)),
        "systems": systems,
        "paired_bootstrap": _family_bootstrap(
            expected,
            predictions,
            families,
            conditions=CONFIRMATORY_CONDITIONS,
            resamples=REFINEMENT_BOOTSTRAP_RESAMPLES,
            seed=REFINEMENT_BOOTSTRAP_SEED,
        ),
        "promotion_gates": gates,
        "all_gates_passed": all(gate["passed"] for gate in gates.values()),
    }


def validate_confirmatory_dataset(
    items: Sequence[EndToEndItem],
    *,
    excluded_families: AbstractSet[str],
) -> ConfirmatoryDatasetSummary:
    """Valida o conjunto novo sem exigir uma segunda anotação externa."""
    if len(items) < MINIMUM_CONFIRMATORY_ITEMS:
        raise EndToEndDatasetError(
            f"A confirmação exige ao menos {MINIMUM_CONFIRMATORY_ITEMS} itens."
        )
    if any(item.split is not DatasetSplit.TEST for item in items):
        raise EndToEndDatasetError("A confirmação deve conter somente itens de teste novos.")
    if any(item.status is not DatasetStatus.REVIEWED for item in items):
        raise EndToEndDatasetError("Todo item confirmatório precisa de curadoria concluída.")
    if any(not item.claim_family for item in items):
        raise EndToEndDatasetError("Todo item confirmatório precisa de família.")
    if any(item.primary_label is not item.label for item in items):
        raise EndToEndDatasetError("O rótulo final deve preservar o gabarito pré-execução.")
    if any(not item.reviewer or not item.reviewed_at for item in items):
        raise EndToEndDatasetError("A proveniência da curadoria precisa estar registrada.")

    labels = Counter(item.label.value for item in items)
    expected_labels = {verdict.value for verdict in Verdict}
    if set(labels) != expected_labels:
        raise EndToEndDatasetError("A confirmação precisa representar as quatro classes.")
    if any(labels[label] < MINIMUM_ITEMS_PER_LABEL for label in expected_labels):
        raise EndToEndDatasetError(
            f"Cada classe exige ao menos {MINIMUM_ITEMS_PER_LABEL} itens."
        )

    grouped: defaultdict[str, list[EndToEndItem]] = defaultdict(list)
    for item in items:
        grouped[item.claim_family or ""].append(item)
    if len(grouped) < MINIMUM_NOVEL_FAMILIES:
        raise EndToEndDatasetError(
            f"A confirmação exige ao menos {MINIMUM_NOVEL_FAMILIES} famílias."
        )
    overlap = sorted(set(grouped) & set(excluded_families))
    if overlap:
        raise EndToEndDatasetError(
            "Famílias reutilizadas de avaliações anteriores: " + ", ".join(overlap)
        )
    for family, family_items in grouped.items():
        family_labels = {item.label.value for item in family_items}
        if family_labels != expected_labels:
            raise EndToEndDatasetError(
                f"A família {family} não contém um item de cada classe."
            )

    conclusive = tuple(
        item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE
    )
    if any(not item.evidence_chunk_ids or not item.origin_reference for item in conclusive):
        raise EndToEndDatasetError(
            "Todo gabarito conclusivo precisa de evidência e origem rastreável."
        )
    insufficient = tuple(
        item for item in items if item.label is Verdict.INSUFFICIENT_EVIDENCE
    )
    if any(item.evidence_chunk_ids or item.origin_reference for item in insufficient):
        raise EndToEndDatasetError(
            "Abstenções devem representar contexto ausente, sem evidência conclusiva."
        )

    return ConfirmatoryDatasetSummary(
        total=len(items),
        labels=dict(sorted(labels.items())),
        families=len(grouped),
        topics=dict(sorted(Counter(item.topic for item in items).items())),
        evidence_chunks=len(
            {chunk_id for item in conclusive for chunk_id in item.evidence_chunk_ids}
        ),
    )
