from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)

MINIMUM_CALIBRATION_ITEMS = 48
MINIMUM_ITEMS_PER_LABEL = 12
MINIMUM_NOVEL_FAMILIES = 12


@dataclass(frozen=True, slots=True)
class RefinementCalibrationSummary:
    total: int
    labels: dict[str, int]
    families: int
    topics: dict[str, int]
    evidence_chunks: int


def load_family_ids(lines: Iterable[str]) -> frozenset[str]:
    families = {
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not families:
        raise EndToEndDatasetError("A lista de famílias congeladas está vazia.")
    return frozenset(families)


def validate_refinement_calibration(
    items: Sequence[EndToEndItem],
    *,
    frozen_test_families: frozenset[str],
) -> RefinementCalibrationSummary:
    """Valida o lote de calibração sem abrir nem reutilizar o teste congelado."""
    if len(items) < MINIMUM_CALIBRATION_ITEMS:
        raise EndToEndDatasetError(
            f"A calibração exige ao menos {MINIMUM_CALIBRATION_ITEMS} itens."
        )
    if any(item.split is not DatasetSplit.DEVELOPMENT for item in items):
        raise EndToEndDatasetError("A calibração não pode conter itens de teste.")
    if any(item.status is not DatasetStatus.DRAFT for item in items):
        raise EndToEndDatasetError(
            "O pacote candidato deve permanecer rascunho até a revisão humana."
        )
    if any(not item.claim_family for item in items):
        raise EndToEndDatasetError("Todo item de calibração precisa de família.")

    labels = Counter(item.label.value for item in items)
    expected_labels = {verdict.value for verdict in Verdict}
    if set(labels) != expected_labels:
        raise EndToEndDatasetError("A calibração precisa representar as quatro classes.")
    if any(labels[label] < MINIMUM_ITEMS_PER_LABEL for label in expected_labels):
        raise EndToEndDatasetError(
            f"Cada classe exige ao menos {MINIMUM_ITEMS_PER_LABEL} itens."
        )

    grouped: defaultdict[str, list[EndToEndItem]] = defaultdict(list)
    for item in items:
        grouped[item.claim_family or ""].append(item)
    if len(grouped) < MINIMUM_NOVEL_FAMILIES:
        raise EndToEndDatasetError(
            f"A calibração exige ao menos {MINIMUM_NOVEL_FAMILIES} famílias."
        )
    overlap = sorted(set(grouped) & frozen_test_families)
    if overlap:
        raise EndToEndDatasetError(
            "Famílias reutilizadas do teste congelado: " + ", ".join(overlap)
        )

    for family, family_items in grouped.items():
        family_labels = {item.label.value for item in family_items}
        if family_labels != expected_labels:
            raise EndToEndDatasetError(
                f"A família {family} não contém uma proposta de cada classe."
            )

    conclusive = tuple(
        item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE
    )
    if any(not item.evidence_chunk_ids or not item.origin_reference for item in conclusive):
        raise EndToEndDatasetError(
            "Toda proposta conclusiva precisa de evidência e origem rastreável."
        )

    return RefinementCalibrationSummary(
        total=len(items),
        labels=dict(sorted(labels.items())),
        families=len(grouped),
        topics=dict(sorted(Counter(item.topic for item in items).items())),
        evidence_chunks=len(
            {chunk_id for item in conclusive for chunk_id in item.evidence_chunk_ids}
        ),
    )
