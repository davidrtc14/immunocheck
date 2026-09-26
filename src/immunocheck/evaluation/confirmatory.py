from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)

MINIMUM_CONFIRMATORY_ITEMS = 32
MINIMUM_ITEMS_PER_LABEL = 8
MINIMUM_NOVEL_FAMILIES = 8


@dataclass(frozen=True, slots=True)
class ConfirmatoryDatasetSummary:
    total: int
    labels: dict[str, int]
    families: int
    topics: dict[str, int]
    evidence_chunks: int


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
