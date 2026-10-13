from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    EndToEndDatasetError,
    load_end_to_end_items,
    validate_end_to_end_items,
)
from immunocheck.evaluation.v4_dataset import validate_v4_dataset

ITEMS_PATH = Path(__file__).parents[1] / "evaluation/refinement_v4/items.jsonl"


@pytest.fixture(scope="module")
def items():
    return load_end_to_end_items(ITEMS_PATH, require_reviewed=True)


def test_committed_v4_dataset_satisfies_all_structural_rules(items) -> None:
    summary = validate_v4_dataset(items, excluded_families=set())

    assert summary.total == 96 and summary.families == 24
    assert set(summary.labels.values()) == {24}
    assert summary.splits == {"development": 48, "test": 48}
    assert summary.public_pattern_items >= 6
    assert all(count >= 6 for count in summary.abstention_types.values())


def test_evidence_must_exist_in_corpus(items) -> None:
    with pytest.raises(EndToEndDatasetError, match="ausente do corpus"):
        validate_v4_dataset(items, excluded_families=set(), valid_chunk_ids={"outro:p1:c1:x"})


def test_reused_families_and_claims_are_rejected(items) -> None:
    family = items[0].claim_family
    with pytest.raises(EndToEndDatasetError, match="Famílias reutilizadas"):
        validate_v4_dataset(items, excluded_families={family})
    with pytest.raises(EndToEndDatasetError, match="Alegações reutilizadas"):
        validate_v4_dataset(items, excluded_families=set(), excluded_claims={items[3].claim.upper()})


def test_too_small_or_unbalanced_dataset_is_rejected(items) -> None:
    with pytest.raises(EndToEndDatasetError, match="ao menos 96"):
        validate_v4_dataset(items[:-4], excluded_families=set())

    supported = next(i for i in items if i.label is Verdict.SUPPORTED)
    swapped = tuple(
        replace(i, label=Verdict.REFUTED, primary_label=Verdict.REFUTED) if i is supported else i
        for i in items
    )
    with pytest.raises(EndToEndDatasetError):
        validate_v4_dataset(swapped, excluded_families=set())


def test_repetitive_template_is_rejected(items) -> None:
    templated = tuple(
        replace(i, claim="A vacina X é segura " + i.claim.split(",")[0][:30] + f" {n}")
        for n, i in enumerate(items)
    )
    with pytest.raises(EndToEndDatasetError, match="Molde repetitivo"):
        validate_v4_dataset(templated, excluded_families=set())


def test_abstention_cannot_carry_evidence_and_family_cannot_cross_splits(items) -> None:
    abstention = next(i for i in items if i.label is Verdict.INSUFFICIENT_EVIDENCE)
    bad = tuple(
        replace(i, origin_reference="doc") if i is abstention else i for i in items
    )
    with pytest.raises(EndToEndDatasetError, match="abstenção não pode ter evidência"):
        validate_v4_dataset(bad, excluded_families=set())

    moved = tuple(
        replace(i, split=DatasetSplit.TEST) if i.item_id == items[0].item_id else i
        for i in items
    )
    with pytest.raises(EndToEndDatasetError, match="desenvolvimento e teste"):
        validate_end_to_end_items(moved)
