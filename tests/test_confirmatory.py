from __future__ import annotations

from dataclasses import replace

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.confirmatory import validate_confirmatory_dataset
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)


def _items() -> tuple[EndToEndItem, ...]:
    result = []
    for family_index in range(8):
        for label in Verdict:
            insufficient = label is Verdict.INSUFFICIENT_EVIDENCE
            result.append(
                EndToEndItem(
                    item_id=f"c-{family_index}-{label.value}",
                    claim=f"alegação {family_index} {label.value}",
                    label=label,
                    topic="tema",
                    split=DatasetSplit.TEST,
                    status=DatasetStatus.REVIEWED,
                    atomic=True,
                    evidence_chunk_ids=() if insufficient else (f"chunk-{family_index}",),
                    rationale="justificativa",
                    origin_type=(
                        "synthetic_missing_context"
                        if insufficient
                        else "synthetic_source_grounded"
                    ),
                    origin_reference=None if insufficient else f"doc-{family_index}",
                    reviewer="project_researcher_ai_assisted",
                    reviewed_at="2026-09-26",
                    second_reviewer=None,
                    second_label=None,
                    second_reviewed_at=None,
                    adjudicator=None,
                    adjudicated_at=None,
                    notes="curadoria documental",
                    claim_family=f"family-{family_index}",
                    primary_label=label,
                    adjudication_basis=None,
                )
            )
    return tuple(result)


def test_accepts_balanced_source_grounded_dataset_without_external_review() -> None:
    summary = validate_confirmatory_dataset(_items(), excluded_families=frozenset())
    assert summary.total == 32
    assert summary.families == 8
    assert summary.labels == {label.value: 8 for label in Verdict}


def test_rejects_family_seen_in_prior_evaluation() -> None:
    with pytest.raises(EndToEndDatasetError, match="reutilizadas"):
        validate_confirmatory_dataset(_items(), excluded_families={"family-3"})


def test_rejects_conclusive_item_without_documentary_evidence() -> None:
    items = list(_items())
    target = next(index for index, item in enumerate(items) if item.label is Verdict.SUPPORTED)
    items[target] = replace(items[target], evidence_chunk_ids=())
    with pytest.raises(EndToEndDatasetError, match="evidência"):
        validate_confirmatory_dataset(tuple(items), excluded_families=frozenset())
