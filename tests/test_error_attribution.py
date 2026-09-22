from __future__ import annotations

from copy import deepcopy

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.error_attribution import (
    analyze_development_error_attribution,
    render_error_attribution_markdown,
)
from tests.test_development_end_to_end import records_for_development


def test_error_attribution_separates_auditor_regression_and_recovery() -> None:
    items, base_records = records_for_development()
    records = deepcopy(base_records)
    first_expected = records[0]["expected_label"]
    second_expected = records[1]["expected_label"]

    records[0]["conditions"]["dense_with_auditor"]["verdict"] = (
        Verdict.INSUFFICIENT_EVIDENCE.value
        if first_expected != Verdict.INSUFFICIENT_EVIDENCE.value
        else Verdict.REFUTED.value
    )
    wrong_second = next(value.value for value in Verdict if value.value != second_expected)
    records[1]["conditions"]["dense_no_auditor"]["verdict"] = wrong_second

    report = analyze_development_error_attribution(records, items)

    assert report["scope"] == "development_outputs_only_no_test_predictions_loaded"
    assert report["auditor_transitions"]["auditor_regression"] == 1
    assert report["auditor_transitions"]["auditor_recovery"] == 1
    assert report["primary_stage_counts"]["auditor_regression"] == 1


def test_error_attribution_detects_material_extraction_loss() -> None:
    items, base_records = records_for_development()
    records = deepcopy(base_records)
    records[0]["extraction"]["claim"] = "vacina"

    report = analyze_development_error_attribution(records, items)

    assert report["extraction"]["low_token_recall_below_0_8"] == 1
    assert report["primary_stage_counts"]["extraction_integrity_risk"] == 1
    markdown = render_error_attribution_markdown(report)
    assert "previsões e métricas do teste não são carregadas" in markdown
    assert "Auditoria de erros" in markdown
