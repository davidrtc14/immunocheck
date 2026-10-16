from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.paraphrase_set import (
    ParaphraseSetError,
    consistency_rate,
    load_paraphrases,
    validate_paraphrases,
)

ROOT = Path(__file__).parents[1]
ITEMS_PATH = ROOT / "evaluation/refinement_v4/items.jsonl"
PARAPHRASES_PATH = ROOT / "evaluation/refinement_v5/paraphrases.jsonl"


@pytest.fixture(scope="module")
def parents():
    return load_end_to_end_items(ITEMS_PATH, require_reviewed=True)


@pytest.fixture(scope="module")
def paraphrases():
    return load_paraphrases(PARAPHRASES_PATH)


def test_committed_paraphrases_are_valid(parents, paraphrases) -> None:
    validate_paraphrases(paraphrases, parents)
    assert len(paraphrases) == 2 * len(parents) == 192


def _swap(paraphrases, index, **changes):
    changed = list(paraphrases)
    changed[index] = replace(changed[index], **changes)
    return changed


def test_label_must_be_inherited(parents, paraphrases) -> None:
    other = "SUPPORTED" if paraphrases[0].label != "SUPPORTED" else "REFUTED"
    with pytest.raises(ParaphraseSetError, match="metadados"):
        validate_paraphrases(_swap(paraphrases, 0, label=other), parents)


def test_numbers_must_be_preserved(parents, paraphrases) -> None:
    index = next(i for i, p in enumerate(paraphrases) if p.parent_item_id == "ref4-0039")
    changed = _swap(paraphrases, index, claim="O DPNI fixou meta de apenas 40% para idosos.")
    with pytest.raises(ParaphraseSetError, match="números ausentes"):
        validate_paraphrases(changed, parents)


def test_negation_must_be_preserved(parents, paraphrases) -> None:
    index = next(i for i, p in enumerate(paraphrases) if p.parent_item_id == "ref4-0074")
    changed = _swap(paraphrases, index, claim="Gestantes devem receber vacinas de vírus vivos.")
    with pytest.raises(ParaphraseSetError, match="negação"):
        validate_paraphrases(changed, parents)


def test_universal_quantifier_must_be_preserved(parents, paraphrases) -> None:
    index = next(i for i, p in enumerate(paraphrases) if p.parent_item_id == "ref4-0028")
    changed = _swap(paraphrases, index, claim="A vacina do SUS protege contra o HPV.")
    with pytest.raises(ParaphraseSetError, match="universal"):
        validate_paraphrases(changed, parents)


def test_missing_style_is_rejected(parents, paraphrases) -> None:
    with pytest.raises(ParaphraseSetError, match="duas paráfrases"):
        validate_paraphrases(paraphrases[1:], parents)


def test_identical_text_is_rejected(parents, paraphrases) -> None:
    parent = next(p for p in parents if p.item_id == paraphrases[0].parent_item_id)
    with pytest.raises(ParaphraseSetError, match="idêntico"):
        validate_paraphrases(_swap(paraphrases, 0, claim=parent.claim), parents)


def test_consistency_rate_counts_failures_as_divergent() -> None:
    predictions = {
        "a": {"original": "SUPPORTED", "colloquial": "SUPPORTED", "formal": "SUPPORTED"},
        "b": {"original": "SUPPORTED", "colloquial": "REFUTED", "formal": "SUPPORTED"},
        "c": {"original": None, "colloquial": None, "formal": None},
        "d": {"original": "MISLEADING", "colloquial": "MISLEADING", "formal": "MISLEADING"},
    }
    assert consistency_rate(predictions) == 0.5


def test_consistency_rate_requires_all_forms() -> None:
    with pytest.raises(ValueError, match="incompletas"):
        consistency_rate({"a": {"original": "SUPPORTED", "formal": "SUPPORTED"}})
