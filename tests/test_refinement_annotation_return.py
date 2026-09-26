from __future__ import annotations

import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.adjudication import (
    load_adjudication_decisions,
    pending_decision_ids,
)
from immunocheck.evaluation.annotation_agreement import (
    compute_annotation_agreement,
    load_annotation_responses,
)
from immunocheck.evaluation.end_to_end import (
    load_end_to_end_items,
    serialize_end_to_end_items,
)
from immunocheck.evaluation.refinement_annotation_return import (
    HUMAN_ATTESTATIONS,
    inspect_refinement_annotation_return,
    inspect_refinement_correction,
    merge_refinement_correction,
)

ROOT = Path(__file__).parents[1]
BASE = ROOT / "evaluation" / "refinement_v2" / "calibration"


def _expected_tasks():
    items = {
        item.item_id: item
        for item in load_end_to_end_items(BASE / "reviewed_items.jsonl", require_reviewed=True)
    }
    manifest = json.loads(
        (BASE / "independent_review" / "selection_manifest.json").read_text(encoding="utf-8")
    )
    return {entry["task_id"]: items[entry["item_id"]] for entry in manifest["mapping"]}


def _complete_human_return() -> str:
    text = (BASE / "independent_review" / "participant" / "ANNOTATIONS.md").read_text(
        encoding="utf-8"
    )
    for statement in HUMAN_ATTESTATIONS:
        text = text.replace(f"- [ ] {statement}", f"- [x] {statement}")
    text = text.replace(
        "- Código interno do revisor:\n", "- Código interno do revisor: second_human_001\n"
    )
    text = text.replace("- Data da revisão:\n", "- Data da revisão: 2026-09-22\n")
    for item in _expected_tasks().values():
        assert item.primary_label is not None
        text = text.replace("- Rótulo:\n", f"- Rótulo: {item.primary_label.value}\n", 1)
        text = text.replace("- Justificativa:\n", "- Justificativa: julgamento próprio.\n", 1)
        text = text.replace(
            "- Fontes e trechos/páginas consultados:\n",
            "- Fontes e trechos/páginas consultados: fonte e trecho conferidos.\n",
            1,
        )
        text = text.replace(
            "- Dúvidas ou ambiguidade:\n", "- Dúvidas ou ambiguidade: nenhuma.\n", 1
        )
    return text


def test_complete_human_return_is_eligible_and_agreement_is_pre_adjudication() -> None:
    inspection = inspect_refinement_annotation_return(
        _complete_human_return(), expected_tasks=_expected_tasks()
    )

    assert inspection.eligible_for_human_gate is True
    assert inspection.reviewer == "second_human_001"
    assert len(inspection.responses) == 16
    assert inspection.agreement == {
        "total": 16,
        "agreement_count": 16,
        "disagreement_count": 0,
        "disagreement_task_ids": [],
        "observed_agreement": 1.0,
        "cohens_kappa": 1.0,
        "valid_for_interhuman_agreement": True,
    }


def test_explicit_ai_return_cannot_close_human_gate() -> None:
    text = _complete_human_return().replace(
        "second_human_001", "IA-assistente (não é anotação humana)"
    )

    inspection = inspect_refinement_annotation_return(text, expected_tasks=_expected_tasks())

    assert inspection.eligible_for_human_gate is False
    assert "explicit_nonhuman_reviewer" in inspection.rejection_reasons
    assert "invalid_reviewer_code" in inspection.rejection_reasons
    assert inspection.agreement is not None
    assert inspection.agreement["observed_agreement"] == 1.0
    assert inspection.agreement["valid_for_interhuman_agreement"] is False


def test_checkbox_spacing_and_brazilian_date_are_normalized() -> None:
    text = (
        _complete_human_return()
        .replace("- [x]", "- [ x ]")
        .replace("- Data da revisão: 2026-09-22", "- Data da revisão:23/09/2026")
    )

    inspection = inspect_refinement_annotation_return(text, expected_tasks=_expected_tasks())

    assert inspection.eligible_for_human_gate is True
    assert inspection.reviewed_at == "2026-09-23"


def test_changed_claim_invalidates_mapping_and_agreement() -> None:
    text = _complete_human_return().replace(
        "A revisão não encontrou impacto nem efetividade",
        "A revisão encontrou impacto e efetividade",
        1,
    )

    inspection = inspect_refinement_annotation_return(text, expected_tasks=_expected_tasks())

    assert inspection.eligible_for_human_gate is False
    assert "changed_claim:ref2-annotation-001" in inspection.rejection_reasons
    assert inspection.agreement is not None
    assert inspection.agreement["valid_for_interhuman_agreement"] is False


def test_published_attempt_002_is_bound_and_pending_only_claim_correction() -> None:
    attempts = BASE / "independent_review" / "attempts"
    receipt = json.loads((attempts / "attempt_002_receipt.json").read_text(encoding="utf-8"))
    raw = (attempts / receipt["raw_return_path"]).read_text(encoding="utf-8-sig")
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")

    inspection = inspect_refinement_annotation_return(raw, expected_tasks=_expected_tasks())

    assert (
        hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        == receipt["source_normalized_sha256"]
    )
    assert inspection.reviewer == "rv0067"
    assert inspection.reviewed_at == "2026-09-23"
    assert inspection.rejection_reasons == ("changed_claim:ref2-annotation-010",)
    assert inspection.agreement is not None
    assert inspection.agreement["agreement_count"] == 12
    assert inspection.agreement["cohens_kappa"] == 2 / 3


def test_technical_dossier_records_completed_human_decisions() -> None:
    independent = BASE / "independent_review"
    receipt = json.loads(
        (independent / "attempts" / "attempt_002_receipt.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (independent / "adjudication" / "technical_audit.json").read_text(encoding="utf-8")
    )
    manifest = json.loads((independent / "selection_manifest.json").read_text(encoding="utf-8"))
    mapping = {entry["task_id"]: entry for entry in manifest["mapping"]}

    assert audit["source_return_sha256"] == receipt["source_normalized_sha256"]
    assert set(audit["ready_task_ids"]) == {
        "ref2-annotation-003",
        "ref2-annotation-011",
        "ref2-annotation-012",
    }
    correction_receipt = json.loads(
        (independent / "attempts" / "attempt_002_correction_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["source_correction_sha256"] == correction_receipt["source_normalized_sha256"]
    assert audit["pending_task_ids"] == []
    assert audit["pre_adjudication_agreement"]["cohens_kappa"] == 0.75
    assert audit["human_final_decisions"] == 3
    assert audit["pipeline_predictions_loaded"] == 0
    assert audit["primary_snapshot_changed"] is False
    assert audit["adjudicated_snapshot_created"] is True
    for recommendation in audit["recommendations"]:
        selected = mapping[recommendation["task_id"]]
        assert recommendation["item_id"] == selected["item_id"]
        assert recommendation["primary_label"] == selected["primary_label"]


def test_published_correction_closes_claim_integrity_and_finalizes_agreement() -> None:
    independent = BASE / "independent_review"
    attempts = independent / "attempts"
    original = inspect_refinement_annotation_return(
        (attempts / "ATTEMPT_002_RETURN.md").read_text(encoding="utf-8-sig"),
        expected_tasks=_expected_tasks(),
    )
    correction_path = attempts / "ATTEMPT_002_CORRECTION_RETURN.md"
    correction = inspect_refinement_correction(
        correction_path.read_text(encoding="utf-8-sig"),
        expected_task_id="ref2-annotation-010",
        expected_task=_expected_tasks()["ref2-annotation-010"],
        expected_reviewer="rv0067",
    )
    merged = merge_refinement_correction(original, correction, expected_tasks=_expected_tasks())

    assert correction.eligible_for_merge is True
    assert correction.corrected_at == "2026-09-24"
    assert correction.response is not None
    assert correction.response.second_label.value == "INSUFFICIENT_EVIDENCE"
    assert merged.eligible_for_human_gate is True
    assert merged.agreement == {
        "total": 16,
        "agreement_count": 13,
        "disagreement_count": 3,
        "disagreement_task_ids": [
            "ref2-annotation-003",
            "ref2-annotation-011",
            "ref2-annotation-012",
        ],
        "observed_agreement": 0.8125,
        "cohens_kappa": 0.75,
        "valid_for_interhuman_agreement": True,
    }


def test_published_accepted_round_and_adjudication_package_are_bound() -> None:
    independent = BASE / "independent_review"
    receipt = json.loads((independent / "review_receipt.json").read_text(encoding="utf-8"))
    agreement = json.loads(
        (independent / "returns" / "agreement_round_001.json").read_text(encoding="utf-8")
    )
    tasks = (independent / "adjudication" / "TASKS.md").read_text(encoding="utf-8")

    assert receipt["secondary_annotation_accepted"] is True
    assert receipt["adjudication_completed"] is False
    assert receipt["adjudication_task_ids"] == agreement["disagreement_task_ids"]
    assert agreement["agreement_count"] == 13
    assert agreement["cohens_kappa"] == 0.75
    assert tasks.count("### Decisão humana a preencher") == 3
    assert "## ref2-annotation-010" not in tasks
    expected = _expected_tasks()
    responses = load_annotation_responses(
        independent / "returns" / "round_001.jsonl", expected_tasks=expected
    )
    computed = compute_annotation_agreement(
        {task_id: item.primary_label for task_id, item in expected.items()}, responses
    )
    assert computed == agreement
    adjudication_tasks = {
        task_id: expected[task_id].item_id for task_id in receipt["adjudication_task_ids"]
    }
    decisions = load_adjudication_decisions(
        independent / "adjudication" / "TASKS.md",
        expected_tasks=adjudication_tasks,
        expected_claims={task_id: expected[task_id].claim for task_id in adjudication_tasks},
    )
    assert pending_decision_ids(decisions) == tuple(receipt["adjudication_task_ids"])
    for entry in receipt["files"]:
        path = independent / entry["path"]
        normalized = path.read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(normalized).hexdigest() == entry["sha256"]


def test_published_adjudication_snapshot_preserves_primary_and_applies_ledger() -> None:
    independent = BASE / "independent_review"
    receipt = json.loads(
        (independent / "adjudication" / "adjudication_receipt.json").read_text(encoding="utf-8")
    )
    primary = load_end_to_end_items(BASE / "reviewed_items.jsonl", require_reviewed=True)
    adjudicated = load_end_to_end_items(BASE / "adjudicated_items.jsonl", require_reviewed=True)
    primary_by_id = {item.item_id: item for item in primary}

    assert len(adjudicated) == 48
    assert sum(item.second_reviewer is not None for item in adjudicated) == 16
    assert sum(item.adjudicator is not None for item in adjudicated) == 3
    assert {item.adjudicator for item in adjudicated if item.adjudicator} == {"project_author"}
    assert all(item.label is primary_by_id[item.item_id].label for item in adjudicated)
    assert all(item.claim == primary_by_id[item.item_id].claim for item in adjudicated)
    assert receipt["primary_snapshot_changed"] is False
    assert receipt["excluded_item_ids"] == []
    assert (
        receipt["adjudicated_snapshot_sha256"]
        == hashlib.sha256(serialize_end_to_end_items(adjudicated).encode("utf-8")).hexdigest()
    )
    decision_path = independent / receipt["decision_file"]
    normalized = decision_path.read_bytes().replace(b"\r\n", b"\n")
    assert receipt["decision_file_sha256"] == hashlib.sha256(normalized).hexdigest()
