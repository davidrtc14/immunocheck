"""Validação do conjunto lacrado v4: calibração (development) e holdout (test) por família."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)

MINIMUM_V4_ITEMS = 96
MINIMUM_V4_FAMILIES = 24
MINIMUM_ITEMS_PER_LABEL = 24
MINIMUM_ITEMS_PER_SPLIT = 48
MINIMUM_ITEMS_PER_LABEL_PER_SPLIT = 12
MINIMUM_PUBLIC_PATTERN_ITEMS = 6
MINIMUM_ITEMS_PER_ABSTENTION_TYPE = 6
MAXIMUM_PREFIX_SHARE = 0.15
MAXIMUM_PAIRWISE_JACCARD = 0.60
CONCLUSIVE_ORIGINS = frozenset({"synthetic_source_grounded", "public_pattern_rewritten"})
ABSTENTION_ORIGINS = frozenset({"abstention_out_of_corpus", "abstention_individual_event"})
PREFIX_TOKENS = 3

_TOKEN = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class V4DatasetSummary:
    total: int
    families: int
    labels: dict[str, int]
    splits: dict[str, int]
    public_pattern_items: int
    abstention_types: dict[str, int]
    max_prefix_share: float
    max_pairwise_jaccard: float


def validate_v4_dataset(
    items: Sequence[EndToEndItem],
    *,
    excluded_families: Collection[str],
    excluded_claims: Collection[str] = (),
    valid_chunk_ids: Collection[str] | None = None,
) -> V4DatasetSummary:
    if len(items) < MINIMUM_V4_ITEMS:
        raise EndToEndDatasetError(f"O v4 exige ao menos {MINIMUM_V4_ITEMS} itens.")
    if any(item.status is not DatasetStatus.REVIEWED for item in items):
        raise EndToEndDatasetError("Todo item v4 precisa de curadoria concluída.")
    if any(not item.claim_family for item in items):
        raise EndToEndDatasetError("Todo item v4 precisa de família.")
    if any(item.primary_label is not item.label for item in items):
        raise EndToEndDatasetError("O rótulo final deve preservar o gabarito pré-execução.")
    if any(not item.reviewer or not item.reviewed_at for item in items):
        raise EndToEndDatasetError("A proveniência da curadoria precisa estar registrada.")

    labels = Counter(item.label.value for item in items)
    expected_labels = {verdict.value for verdict in Verdict}
    if set(labels) != expected_labels or any(
        count < MINIMUM_ITEMS_PER_LABEL for count in labels.values()
    ):
        raise EndToEndDatasetError(
            f"Cada classe exige ao menos {MINIMUM_ITEMS_PER_LABEL} itens."
        )
    if len(set(labels.values())) != 1:
        raise EndToEndDatasetError("As quatro classes devem estar balanceadas.")

    splits = Counter(item.split.value for item in items)
    if set(splits) != {split.value for split in DatasetSplit} or any(
        count < MINIMUM_ITEMS_PER_SPLIT for count in splits.values()
    ):
        raise EndToEndDatasetError(
            f"Calibração e holdout exigem ao menos {MINIMUM_ITEMS_PER_SPLIT} itens cada."
        )
    for split in DatasetSplit:
        per_label = Counter(item.label.value for item in items if item.split is split)
        if set(per_label) != expected_labels or any(
            count < MINIMUM_ITEMS_PER_LABEL_PER_SPLIT for count in per_label.values()
        ):
            raise EndToEndDatasetError(
                f"A partição {split.value} precisa de {MINIMUM_ITEMS_PER_LABEL_PER_SPLIT} "
                "itens por classe."
            )

    grouped: defaultdict[str, list[EndToEndItem]] = defaultdict(list)
    for item in items:
        grouped[item.claim_family or ""].append(item)
    if len(grouped) < MINIMUM_V4_FAMILIES:
        raise EndToEndDatasetError(f"O v4 exige ao menos {MINIMUM_V4_FAMILIES} famílias.")
    overlap = sorted(set(grouped) & set(excluded_families))
    if overlap:
        raise EndToEndDatasetError("Famílias reutilizadas: " + ", ".join(overlap))
    for family, family_items in grouped.items():
        if Counter(item.label.value for item in family_items) != Counter(
            {label: 1 for label in expected_labels}
        ):
            raise EndToEndDatasetError(f"A família {family} deve ter um item de cada classe.")

    normalized_excluded = {_normalize(claim) for claim in excluded_claims}
    reused = sorted(item.item_id for item in items if _normalize(item.claim) in normalized_excluded)
    if reused:
        raise EndToEndDatasetError("Alegações reutilizadas de avaliações anteriores: " + ", ".join(reused))

    conclusive = [item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE]
    for item in conclusive:
        if not item.evidence_chunk_ids or not item.origin_reference:
            raise EndToEndDatasetError(f"{item.item_id}: gabarito conclusivo sem evidência/origem.")
        if item.origin_type not in CONCLUSIVE_ORIGINS:
            raise EndToEndDatasetError(f"{item.item_id}: origem conclusiva inválida.")
    abstentions = [item for item in items if item.label is Verdict.INSUFFICIENT_EVIDENCE]
    for item in abstentions:
        if item.evidence_chunk_ids or item.origin_reference:
            raise EndToEndDatasetError(f"{item.item_id}: abstenção não pode ter evidência.")
        if item.origin_type not in ABSTENTION_ORIGINS:
            raise EndToEndDatasetError(f"{item.item_id}: tipo de abstenção inválido.")
    abstention_types = Counter(item.origin_type for item in abstentions)
    if any(abstention_types[kind] < MINIMUM_ITEMS_PER_ABSTENTION_TYPE for kind in ABSTENTION_ORIGINS):
        raise EndToEndDatasetError(
            f"Cada tipo de abstenção exige ao menos {MINIMUM_ITEMS_PER_ABSTENTION_TYPE} itens."
        )
    public_pattern = sum(item.origin_type == "public_pattern_rewritten" for item in items)
    if public_pattern < MINIMUM_PUBLIC_PATTERN_ITEMS:
        raise EndToEndDatasetError(
            f"Exige ao menos {MINIMUM_PUBLIC_PATTERN_ITEMS} alegações reescritas de padrões públicos."
        )

    if valid_chunk_ids is not None:
        known = set(valid_chunk_ids)
        unknown = sorted(c for item in items for c in item.evidence_chunk_ids if c not in known)
        if unknown:
            raise EndToEndDatasetError("Evidência ausente do corpus: " + ", ".join(unknown))

    prefix_share = _max_prefix_share(items)
    if prefix_share > MAXIMUM_PREFIX_SHARE:
        raise EndToEndDatasetError(
            f"Molde repetitivo: {prefix_share:.2f} das alegações compartilham o mesmo início."
        )
    jaccard = _max_pairwise_jaccard(items)
    if jaccard > MAXIMUM_PAIRWISE_JACCARD:
        raise EndToEndDatasetError(f"Alegações quase idênticas (Jaccard {jaccard:.2f}).")

    return V4DatasetSummary(
        total=len(items),
        families=len(grouped),
        labels=dict(sorted(labels.items())),
        splits=dict(sorted(splits.items())),
        public_pattern_items=public_pattern,
        abstention_types=dict(sorted(abstention_types.items())),
        max_prefix_share=prefix_share,
        max_pairwise_jaccard=jaccard,
    )


def _normalize(claim: str) -> str:
    return " ".join(claim.casefold().split())


def _tokens(claim: str) -> list[str]:
    return _TOKEN.findall(claim.casefold())


def _max_prefix_share(items: Sequence[EndToEndItem]) -> float:
    prefixes = Counter(tuple(_tokens(item.claim)[:PREFIX_TOKENS]) for item in items)
    return max(prefixes.values()) / len(items)


def _max_pairwise_jaccard(items: Sequence[EndToEndItem]) -> float:
    """Maior similaridade entre alegações de famílias diferentes (dentro da família é esperada)."""
    token_sets = [set(_tokens(item.claim)) for item in items]
    best = 0.0
    for index, left in enumerate(token_sets):
        for other in range(index + 1, len(token_sets)):
            if items[index].claim_family == items[other].claim_family:
                continue
            right = token_sets[other]
            union = left | right
            if union:
                best = max(best, len(left & right) / len(union))
    return best
