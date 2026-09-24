from __future__ import annotations

import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_annotation_return import (
    HUMAN_ATTESTATIONS,
    inspect_refinement_annotation_return,
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
    text = text.replace("- Código interno do revisor:\n", "- Código interno do revisor: second_human_001\n")
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
    text = _complete_human_return().replace("- [x]", "- [ x ]").replace(
        "- Data da revisão: 2026-09-22", "- Data da revisão:23/09/2026"
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

    assert hashlib.sha256(normalized.encode("utf-8")).hexdigest() == receipt[
        "source_normalized_sha256"
    ]
    assert inspection.reviewer == "rv0067"
    assert inspection.reviewed_at == "2026-09-23"
    assert inspection.rejection_reasons == ("changed_claim:ref2-annotation-010",)
    assert inspection.agreement is not None
    assert inspection.agreement["agreement_count"] == 12
    assert inspection.agreement["cohens_kappa"] == 2 / 3


def test_technical_dossier_covers_only_intact_disagreements_without_decisions() -> None:
    independent = BASE / "independent_review"
    receipt = json.loads(
        (independent / "attempts" / "attempt_002_receipt.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (independent / "adjudication" / "technical_audit.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (independent / "selection_manifest.json").read_text(encoding="utf-8")
    )
    mapping = {entry["task_id"]: entry for entry in manifest["mapping"]}

    assert audit["source_return_sha256"] == receipt["source_normalized_sha256"]
    assert set(audit["ready_task_ids"]) == {
        "ref2-annotation-003",
        "ref2-annotation-011",
        "ref2-annotation-012",
    }
    assert audit["pending_task_ids"] == ["ref2-annotation-010"]
    assert audit["human_final_decisions"] == audit["pipeline_predictions_loaded"] == 0
    assert audit["dataset_changed"] is False
    for recommendation in audit["recommendations"]:
        selected = mapping[recommendation["task_id"]]
        assert recommendation["item_id"] == selected["item_id"]
        assert recommendation["primary_label"] == selected["primary_label"]
