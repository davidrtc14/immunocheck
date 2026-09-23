from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.evaluation.end_to_end import (
    DatasetStatus,
    EndToEndDatasetError,
    load_end_to_end_items,
)
from immunocheck.evaluation.refinement_calibration import (
    load_family_ids,
    validate_refinement_calibration,
)

ROOT = Path(__file__).parents[1]
CANDIDATES = ROOT / "evaluation" / "refinement_v2" / "calibration" / "candidates.jsonl"
FROZEN_FAMILIES = ROOT / "evaluation" / "refinement_v2" / "FROZEN_TEST_FAMILIES.txt"


def _package():
    items = load_end_to_end_items(CANDIDATES)
    families = load_family_ids(FROZEN_FAMILIES.read_text(encoding="utf-8").splitlines())
    return items, families


def test_candidate_package_is_balanced_novel_and_still_draft() -> None:
    items, families = _package()

    summary = validate_refinement_calibration(items, frozen_test_families=families)

    assert summary.total == 48
    assert summary.families == 12
    assert set(summary.labels.values()) == {12}
    assert summary.evidence_chunks >= 12


def test_candidate_package_rejects_frozen_test_family() -> None:
    items, families = _package()
    changed = (replace(items[0], claim_family=next(iter(families))), *items[1:])

    with pytest.raises(EndToEndDatasetError, match="teste congelado"):
        validate_refinement_calibration(changed, frozen_test_families=families)


def test_candidate_package_rejects_premature_human_review_claim() -> None:
    items, families = _package()
    changed = (replace(items[0], status=DatasetStatus.REVIEWED), *items[1:])

    with pytest.raises(EndToEndDatasetError, match="rascunho"):
        validate_refinement_calibration(changed, frozen_test_families=families)
