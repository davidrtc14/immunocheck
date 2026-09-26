from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
    load_end_to_end_items,
)
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_CONDITIONS,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)

ROOT = Path(__file__).parents[1]


def _items() -> tuple[EndToEndItem, ...]:
    result = []
    for index, label in enumerate(Verdict, start=1):
        evidence = () if label is Verdict.INSUFFICIENT_EVIDENCE else (f"doc:p1:c1:{index:012x}",)
        result.append(
            EndToEndItem(
                item_id=f"ref2-cal-{index:04d}",
                claim=f"Alegação {index}.",
                label=label,
                topic="fixture",
                split=DatasetSplit.DEVELOPMENT,
                status=DatasetStatus.REVIEWED,
                atomic=True,
                evidence_chunk_ids=evidence,
                rationale="Revisada.",
                origin_type="synthetic_source_grounded",
                origin_reference="doc" if evidence else None,
                reviewer="primary",
                reviewed_at="2026-09-26",
                second_reviewer=None,
                second_label=None,
                second_reviewed_at=None,
                adjudicator=None,
                adjudicated_at=None,
                notes=None,
                claim_family=f"family_{index}",
                primary_label=label,
            )
        )
    return tuple(result)


def _condition(verdict: Verdict, source_ids: tuple[str, ...], *, latency=1_000.0):
    return {
        "verdict": verdict.value,
        "source_ids": list(source_ids),
        "latency_ms": latency,
        "technical_error": None,
    }


def _records(items: tuple[EndToEndItem, ...], *, perfect_candidate: bool):
    records = []
    for item in items:
        baseline = Verdict.SUPPORTED
        candidate = item.label if perfect_candidate else baseline
        records.append(
            {
                "item_id": item.item_id,
                "claim_family": item.claim_family,
                "expected_label": item.label.value,
                "extraction": {
                    "claim": item.claim,
                    "latency_ms": 100.0,
                    "technical_error": None,
                },
                "conditions": {
                    REFINEMENT_CONDITIONS[0]: _condition(
                        baseline,
                        item.evidence_chunk_ids if baseline is item.label else (),
                    ),
                    REFINEMENT_CONDITIONS[1]: _condition(
                        candidate,
                        item.evidence_chunk_ids
                        if candidate is not Verdict.INSUFFICIENT_EVIDENCE
                        else (),
                    ),
                },
            }
        )
    return tuple(records)


def test_summary_applies_preregistered_gates_and_family_bootstrap() -> None:
    items = _items()
    summary = summarize_refinement_records(
        _records(items, perfect_candidate=True),
        items,
        bootstrap_resamples=20,
        seed=7,
    )

    assert summary["systems"][REFINEMENT_CONDITIONS[1]]["macro_f1"] == 1.0
    assert summary["promotion_gates"]["macro_f1_delta"]["passed"] is True
    assert summary["promotion_gates"]["misleading_recall"]["passed"] is True
    assert summary["factual_auditor_condition_eligible"] is True
    assert summary["paired_bootstrap"]["unit"] == "claim_family"


def test_summary_blocks_auditor_when_candidate_does_not_improve() -> None:
    items = _items()
    summary = summarize_refinement_records(
        _records(items, perfect_candidate=False),
        items,
        bootstrap_resamples=10,
        seed=7,
    )

    assert summary["promotion_gates"]["macro_f1_delta"]["passed"] is False
    assert summary["promotion_gates"]["misleading_recall"]["passed"] is False
    assert summary["factual_auditor_condition_eligible"] is False


def test_summary_accepts_explicit_condition_pair() -> None:
    items = _items()
    conditions = ("baseline", "dense_top20")
    records = tuple(
        {
            **record,
            "conditions": {
                conditions[0]: record["conditions"][REFINEMENT_CONDITIONS[0]],
                conditions[1]: record["conditions"][REFINEMENT_CONDITIONS[1]],
            },
        }
        for record in _records(items, perfect_candidate=True)
    )

    summary = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=20,
        seed=7,
        conditions=conditions,
    )

    assert tuple(summary["systems"]) == conditions
    assert summary["systems"][conditions[1]]["macro_f1"] == 1.0
    assert summary["factual_auditor_condition_eligible"] is True


def test_checkpoint_rejects_changed_mapping_or_test_item() -> None:
    items = _items()
    records = _records(items, perfect_candidate=True)
    changed = (replace(items[0], split=DatasetSplit.TEST), *items[1:])
    with pytest.raises(EndToEndDatasetError, match="somente itens de desenvolvimento"):
        validate_refinement_checkpoint(records, changed)

    bad_record = {**records[0], "item_id": "outro"}
    with pytest.raises(EndToEndDatasetError, match="não corresponde"):
        validate_refinement_checkpoint((bad_record, *records[1:]), items)


def test_published_phase_a_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v2"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_phase_a.jsonl"
    report_path = results / "calibration_phase_a.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
    )

    assert report["summary"] == recomputed
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert report["factual_auditor_executed"] is False
    assert report["factual_auditor_next_step"] == "not_eligible_under_preregistered_gates"
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 2
    phase = manifest["experiment_phase_a"]
    assert phase["candidate_promoted"] is phase["factual_auditor_executed"] is False
    assert (
        phase["checkpoint_sha256"]
        == hashlib.sha256(checkpoint_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    )
    assert (
        phase["report_sha256"]
        == hashlib.sha256(report_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    )


def test_published_top20_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v2"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_top20.jsonl"
    report_path = results / "calibration_top20.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    conditions = ("v1_dense_with_auditor", "v2_separated_dense_top20_no_auditor")
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
        conditions=conditions,
    )

    assert report["summary"] == recomputed
    assert report["single_changed_component"] == "dense_retrieval_top_k_6_to_20"
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert report["factual_auditor_executed"] is False
    assert report["factual_auditor_next_step"] == "not_eligible_under_preregistered_gates"
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 1
    experiment = manifest["experiment_top20"]
    assert experiment["candidate_promoted"] is experiment["factual_auditor_executed"] is False
    assert (
        experiment["checkpoint_sha256"]
        == hashlib.sha256(checkpoint_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    )
    assert (
        experiment["report_sha256"]
        == hashlib.sha256(report_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    )


def test_published_direct_top6_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v2"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_direct_top6.jsonl"
    report_path = results / "calibration_direct_top6.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    conditions = ("v1_dense_with_auditor", "v2_direct_dense_top6_no_auditor")
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
        conditions=conditions,
    )

    assert report["summary"] == recomputed
    assert report["single_changed_component_from_baseline"] == "remove_faithfulness_auditor"
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert report["factual_auditor_executed"] is False
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 3
    experiment = manifest["experiment_direct_top6"]
    assert experiment["candidate_promoted"] is experiment["holdout_creation_authorized"] is False
    assert experiment["checkpoint_sha256"] == _normalized_sha256(checkpoint_path)
    assert experiment["report_sha256"] == _normalized_sha256(report_path)


def test_published_relation_v3_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v3"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_relation_top15.jsonl"
    report_path = results / "calibration_relation_top15.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    conditions = ("v1_dense_with_auditor", "v3_relation_dense_top15_no_auditor")
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
        conditions=conditions,
    )

    assert report["summary"] == recomputed
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 4
    experiment = manifest["experiment_relation_v3"]
    assert experiment["candidate_promoted"] is False
    assert experiment["checkpoint_sha256"] == _normalized_sha256(checkpoint_path)
    assert experiment["report_sha256"] == _normalized_sha256(report_path)


def test_published_routed_v3_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v3"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_routed.jsonl"
    report_path = results / "calibration_routed.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    conditions = ("v1_dense_with_auditor", "v3_routed_specialists_no_auditor")
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
        conditions=conditions,
    )

    assert report["summary"] == recomputed
    assert report["v1_test_items_loaded"] == report["holdout_items_loaded"] == 0
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 6
    experiment = manifest["experiment_routed_v3"]
    assert experiment["candidate_promoted"] is False
    assert experiment["checkpoint_sha256"] == _normalized_sha256(checkpoint_path)
    assert experiment["report_sha256"] == _normalized_sha256(report_path)


def test_published_citation_selector_v3_report_is_bound_and_reproducible() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v3"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "calibration_citations.jsonl"
    report_path = results / "calibration_citations.json"
    dataset_path = calibration / "adjudicated_items.jsonl"
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    report = json.loads(report_path.read_text("utf-8"))
    items = load_end_to_end_items(dataset_path, require_reviewed=True)
    records = load_refinement_checkpoint(checkpoint_path)
    conditions = ("v1_dense_with_auditor", "v3_routed_with_citation_selector")
    recomputed = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=2000,
        seed=20260926,
        conditions=conditions,
    )

    assert report["summary"] == recomputed
    assert report["verdict_changes_from_routed"] == 0
    assert sum(gate["passed"] for gate in report["summary"]["promotion_gates"].values()) == 6
    experiment = manifest["experiment_citation_selector_v3"]
    assert experiment["candidate_promoted"] is False
    assert experiment["checkpoint_sha256"] == _normalized_sha256(checkpoint_path)
    assert experiment["report_sha256"] == _normalized_sha256(report_path)


def _normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
