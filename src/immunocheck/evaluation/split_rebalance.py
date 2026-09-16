"""Reestratificação pré-congelamento sem usar previsões ou métricas do sistema."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, replace

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndDatasetError, EndToEndItem


@dataclass(frozen=True, slots=True)
class FamilySwapPlan:
    development_to_test: str
    test_to_development: str
    moved_item_ids: tuple[str, ...]
    development_targets: dict[str, int]
    items: tuple[EndToEndItem, ...]


def class_split_counts(items: tuple[EndToEndItem, ...]) -> dict[str, dict[str, int]]:
    return {
        verdict.value: {
            split.value: sum(item.label is verdict and item.split is split for item in items)
            for split in DatasetSplit
        }
        for verdict in Verdict
    }


def propose_minimal_family_swap(items: tuple[EndToEndItem, ...], *, seed: int) -> FamilySwapPlan:
    """Troca um par mínimo de famílias inteiras para restaurar 60%/40% por classe."""
    if not items or any(not item.claim_family for item in items):
        raise EndToEndDatasetError("A reestratificação exige famílias em todos os itens.")
    families: dict[str, list[EndToEndItem]] = defaultdict(list)
    for item in items:
        families[item.claim_family].append(item)
    if any(len({item.split for item in group}) != 1 for group in families.values()):
        raise EndToEndDatasetError("Uma família já está dividida entre os splits.")

    current_development = Counter(
        item.label for item in items if item.split is DatasetSplit.DEVELOPMENT
    )
    targets = {
        verdict: round(sum(item.label is verdict for item in items) * 0.60) for verdict in Verdict
    }
    if current_development == Counter(targets):
        raise EndToEndDatasetError("O split já atende 60%/40%; nenhuma troca é necessária.")

    development = {
        family: group
        for family, group in families.items()
        if group[0].split is DatasetSplit.DEVELOPMENT
    }
    test = {
        family: group for family, group in families.items() if group[0].split is DatasetSplit.TEST
    }
    candidates: list[tuple[int, str, str, str]] = []
    for dev_family, dev_group in development.items():
        dev_labels = Counter(item.label for item in dev_group)
        for test_family, test_group in test.items():
            if len(dev_group) != len(test_group):
                continue
            resulting = current_development.copy()
            resulting.subtract(dev_labels)
            resulting.update(item.label for item in test_group)
            if resulting != Counter(targets):
                continue
            tie_break = hashlib.sha256(f"{seed}|{dev_family}|{test_family}".encode()).hexdigest()
            candidates.append(
                (len(dev_group) + len(test_group), tie_break, dev_family, test_family)
            )
    if not candidates:
        raise EndToEndDatasetError(
            "Não existe troca de um par de famílias que restaure a estratificação."
        )
    _, _, dev_family, test_family = min(candidates)
    moved = tuple(item.item_id for item in (*development[dev_family], *test[test_family]))
    rebalanced = tuple(
        replace(item, split=DatasetSplit.TEST)
        if item.claim_family == dev_family
        else replace(item, split=DatasetSplit.DEVELOPMENT)
        if item.claim_family == test_family
        else item
        for item in items
    )
    if any(
        len({item.split for item in rebalanced if item.claim_family == family}) != 1
        for family in families
    ):
        raise AssertionError("A troca interna dividiu uma família.")
    if {
        verdict: sum(
            item.label is verdict and item.split is DatasetSplit.DEVELOPMENT for item in rebalanced
        )
        for verdict in Verdict
    } != targets:
        raise AssertionError("A troca interna não atingiu as metas calculadas.")
    return FamilySwapPlan(
        development_to_test=dev_family,
        test_to_development=test_family,
        moved_item_ids=moved,
        development_targets={verdict.value: targets[verdict] for verdict in Verdict},
        items=rebalanced,
    )
