from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetStatus,
    EndToEndDatasetError,
    load_end_to_end_items,
)
from immunocheck.evaluation.refinement_calibration import (
    load_family_ids,
    select_refinement_second_annotation_items,
    validate_refinement_calibration,
)

ROOT = Path(__file__).parents[1]
CANDIDATES = ROOT / "evaluation" / "refinement_v2" / "calibration" / "candidates.jsonl"
FROZEN_FAMILIES = ROOT / "evaluation" / "refinement_v2" / "FROZEN_TEST_FAMILIES.txt"
REVIEWED = ROOT / "evaluation" / "refinement_v2" / "calibration" / "reviewed_items.jsonl"
TARGET_FAMILIES = frozenset(
    {
        "dengue_postmarketing_signal",
        "mpox_notification_severity",
        "measles_first_dose_age_response",
        "hpv_single_dose_scope",
        "meningococcal_conjugate_impact",
        "adult_pneumococcal_vaccine_type_outcomes",
        "enhanced_influenza_evidence_certainty",
        "vaccination_autoimmune_pooled_association",
        "covid_pregnancy_evidence_certainty",
        "vaccine_misinformation_scare_tactics",
        "adjuvant_mechanism_delivery",
        "acellular_pertussis_waning",
    }
)
INDEPENDENT_REVIEW = (
    ROOT / "evaluation" / "refinement_v2" / "calibration" / "independent_review"
)
REVIEWS = ROOT / "evaluation" / "refinement_v2" / "calibration" / "reviews"


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


def test_reviewed_snapshot_preserves_approved_primary_labels() -> None:
    items = load_end_to_end_items(REVIEWED, require_reviewed=True)
    families = load_family_ids(FROZEN_FAMILIES.read_text(encoding="utf-8").splitlines())

    summary = validate_refinement_calibration(
        items,
        frozen_test_families=families,
        expected_status=DatasetStatus.REVIEWED,
    )

    assert summary.total == 48
    assert all(item.primary_label is item.label for item in items)
    assert {item.reviewer for item in items} == {"primary_reviewer_001"}


def test_second_review_selection_is_blind_balanced_and_covers_target_families() -> None:
    items = load_end_to_end_items(REVIEWED, require_reviewed=True)

    selected = select_refinement_second_annotation_items(
        items,
        target_families=TARGET_FAMILIES,
    )

    assert len(selected) == len({item.item_id for item in selected}) == 16
    assert {item.claim_family for item in selected} == TARGET_FAMILIES
    assert {label: sum(item.primary_label is label for item in selected) for label in Verdict} == {
        label: 4 for label in Verdict
    }
    assert selected == select_refinement_second_annotation_items(
        tuple(reversed(items)),
        target_families=TARGET_FAMILIES,
    )


def test_published_second_review_package_is_blind_and_bound_to_final_return() -> None:
    manifest = json.loads(
        (INDEPENDENT_REVIEW / "selection_manifest.json").read_text(encoding="utf-8")
    )
    annotations = (INDEPENDENT_REVIEW / "participant" / "ANNOTATIONS.md").read_text(
        encoding="utf-8"
    )
    receipt = json.loads(
        (REVIEWS / "primary_review_receipt.json").read_text(encoding="utf-8")
    )
    returned = (
        (REVIEWS / "PRIMARY_REVIEW_2026-09-22.md")
        .read_text(encoding="utf-8-sig")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    assert manifest["selected"] == annotations.count("## ref2-annotation-") == 16
    assert manifest["selected_family_count"] == manifest["target_family_count"] == 12
    assert set(manifest["selected_class_counts"].values()) == {4}
    assert receipt["returned_review_normalized_sha256"] == hashlib.sha256(
        returned.encode("utf-8")
    ).hexdigest()
    assert annotations.count("- Rótulo:\n") == 16
    assert "- [ ] Sou uma pessoa" in annotations
    assert "- Código interno do revisor:\n" in annotations
    participant_text = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted((INDEPENDENT_REVIEW / "participant").iterdir())
    )
    assert "ref2-cal-" not in participant_text
    assert "primary_label" not in participant_text
    assert "evidence_chunk_ids" not in participant_text
