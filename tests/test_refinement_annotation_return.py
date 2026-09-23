from __future__ import annotations

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


def test_changed_claim_invalidates_mapping_and_agreement() -> None:
    text = _complete_human_return().replace(
        "A revisão não encontrou impacto nem efetividade",
        "A revisão encontrou impacto e efetividade",
        1,
    )

    inspection = inspect_refinement_annotation_return(text, expected_tasks=_expected_tasks())

    assert inspection.eligible_for_human_gate is False
    assert "changed_claim:ref2-annotation-001" in inspection.rejection_reasons
    assert inspection.agreement is None
