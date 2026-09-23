from __future__ import annotations

import random
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
MINIMUM_SECOND_REVIEW_ITEMS = 15
REFINEMENT_SECOND_ANNOTATION_SEED = 20260922


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
    expected_status: DatasetStatus = DatasetStatus.DRAFT,
) -> RefinementCalibrationSummary:
    """Valida o lote de calibração sem abrir nem reutilizar o teste congelado."""
    if len(items) < MINIMUM_CALIBRATION_ITEMS:
        raise EndToEndDatasetError(
            f"A calibração exige ao menos {MINIMUM_CALIBRATION_ITEMS} itens."
        )
    if any(item.split is not DatasetSplit.DEVELOPMENT for item in items):
        raise EndToEndDatasetError("A calibração não pode conter itens de teste.")
    if any(item.status is not expected_status for item in items):
        if expected_status is DatasetStatus.DRAFT:
            raise EndToEndDatasetError(
                "O pacote candidato deve permanecer rascunho até a revisão humana."
            )
        raise EndToEndDatasetError(
            "O snapshot revisado deve conter apenas itens com status reviewed."
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

    if expected_status is DatasetStatus.REVIEWED and any(
        item.primary_label is not item.label for item in items
    ):
        raise EndToEndDatasetError(
            "A revisão sem exceções deve preservar o rótulo primário de cada item."
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


def select_refinement_second_annotation_items(
    items: Sequence[EndToEndItem],
    *,
    target_families: frozenset[str],
    seed: int = REFINEMENT_SECOND_ANNOTATION_SEED,
) -> tuple[EndToEndItem, ...]:
    """Seleciona amostra cega balanceada e maximiza a cobertura das famílias-alvo."""
    reviewed = tuple(items)
    if len(reviewed) < MINIMUM_CALIBRATION_ITEMS:
        raise EndToEndDatasetError("A seleção exige a calibração revisada completa.")
    if any(
        item.status is not DatasetStatus.REVIEWED or item.primary_label is None
        for item in reviewed
    ):
        raise EndToEndDatasetError("A seleção exige primeira revisão concluída.")
    eligible = tuple(item for item in reviewed if item.claim_family in target_families)
    eligible_families = {item.claim_family for item in eligible}
    if eligible_families != set(target_families):
        raise EndToEndDatasetError("Nem todas as famílias-alvo estão disponíveis.")

    # 30% de 48 são 15 itens; 16 preservam quatro itens por classe.
    target_per_label = (MINIMUM_SECOND_REVIEW_ITEMS + len(Verdict) - 1) // len(Verdict)
    rng = random.Random(seed)
    selected: list[EndToEndItem] = []
    used_families: set[str] = set()
    for label in Verdict:
        candidates = sorted(
            (item for item in eligible if item.primary_label is label),
            key=lambda item: item.item_id,
        )
        rng.shuffle(candidates)
        candidates.sort(key=lambda item: item.claim_family in used_families)
        chosen = candidates[:target_per_label]
        if len(chosen) != target_per_label:
            raise EndToEndDatasetError("A amostra não cobre todas as classes.")
        selected.extend(chosen)
        used_families.update(item.claim_family or "" for item in chosen)
    rng.shuffle(selected)
    if len(selected) < MINIMUM_SECOND_REVIEW_ITEMS:
        raise EndToEndDatasetError("A amostra cobre menos de 30% da calibração.")
    return tuple(selected)
