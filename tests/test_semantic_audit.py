from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)
from immunocheck.evaluation.semantic_audit import rank_cross_split_semantic_pairs


def item(item_id: str, split: DatasetSplit, family: str) -> EndToEndItem:
    return EndToEndItem(
        item_id=item_id,
        claim=f"Alegação {item_id}.",
        label=Verdict.SUPPORTED,
        topic="fixture",
        split=split,
        status=DatasetStatus.REVIEWED,
        atomic=True,
        evidence_chunk_ids=("fixture",),
        rationale="Fixture.",
        origin_type="test_fixture",
        origin_reference=None,
        reviewer="fixture",
        reviewed_at="2026-09-01",
        second_reviewer=None,
        second_label=None,
        second_reviewed_at=None,
        adjudicator=None,
        adjudicated_at=None,
        notes=None,
        claim_family=family,
        primary_label=Verdict.SUPPORTED,
    )


def test_ranks_cross_split_pairs_deterministically():
    items = (
        item("dev-a", DatasetSplit.DEVELOPMENT, "family-a"),
        item("dev-b", DatasetSplit.DEVELOPMENT, "family-b"),
        item("test-a", DatasetSplit.TEST, "family-c"),
        item("test-b", DatasetSplit.TEST, "family-d"),
    )
    vectors = np.asarray(((1, 0), (0, 1), (0.9, 0.1), (0.2, 0.8)), dtype=np.float32)
    result = rank_cross_split_semantic_pairs(items, vectors, limit=2)
    assert [(pair.development_item_id, pair.test_item_id) for pair in result] == [
        ("dev-a", "test-a"),
        ("dev-b", "test-b"),
    ]
    assert result[0].cosine_similarity > result[1].cosine_similarity


@pytest.mark.parametrize(
    "vectors", [np.ones((3, 2)), np.ones((4, 0)), np.asarray(((1, 0), (0, 1), (1, 1), (0, 0)))]
)
def test_rejects_invalid_or_zero_embeddings(vectors):
    items = (
        item("dev-a", DatasetSplit.DEVELOPMENT, "family-a"),
        item("dev-b", DatasetSplit.DEVELOPMENT, "family-b"),
        item("test-a", DatasetSplit.TEST, "family-c"),
        item("test-b", DatasetSplit.TEST, "family-d"),
    )
    with pytest.raises(EndToEndDatasetError):
        rank_cross_split_semantic_pairs(items, np.asarray(vectors, dtype=np.float32))


def test_rejects_family_present_in_both_splits():
    items = (
        item("dev", DatasetSplit.DEVELOPMENT, "shared"),
        item("test", DatasetSplit.TEST, "shared"),
    )
    with pytest.raises(EndToEndDatasetError, match="dois splits"):
        rank_cross_split_semantic_pairs(items, np.eye(2, dtype=np.float32))
    assert replace(items[0], claim="Imutável.").split is DatasetSplit.DEVELOPMENT
