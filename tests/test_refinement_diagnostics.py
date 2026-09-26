from __future__ import annotations

import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_diagnostics import analyze_refinement_phase_a
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint

ROOT = Path(__file__).parents[1]
BASE = ROOT / "evaluation" / "refinement_v2" / "calibration"
RESULTS = ROOT / "evaluation" / "results" / "refinement_v2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_published_phase_a_diagnostics_are_reproducible_and_isolated() -> None:
    dataset = BASE / "adjudicated_items.jsonl"
    records = RESULTS / "calibration_phase_a.jsonl"
    published = json.loads((RESULTS / "calibration_phase_a_diagnostics.json").read_text("utf-8"))
    recomputed = analyze_refinement_phase_a(
        load_refinement_checkpoint(records),
        load_end_to_end_items(dataset, require_reviewed=True),
    )

    assert {key: value for key, value in published.items() if key != "inputs"} == recomputed
    assert sum(published["primary_stage_counts"].values()) == 48
    assert published["inputs"]["dataset_sha256"] == _sha256(dataset)
    assert published["inputs"]["records_sha256"] == _sha256(records)
    assert published["inputs"]["v1_test_records_loaded"] == 0
    assert published["inputs"]["holdout_v2_records_loaded"] == 0


def test_published_retrieval_depth_supports_dense_top20_hypothesis() -> None:
    report = json.loads((RESULTS / "calibration_retrieval_depth.json").read_text("utf-8"))
    inputs = report["inputs"]
    dense = report["systems"]["phase_a_extracted_claim_dense"]["hit_at_k"]
    hybrid = report["systems"]["phase_a_extracted_claim_hybrid_rrf"]["hit_at_k"]

    assert report["v1_test_records_loaded"] == report["holdout_v2_records_loaded"] == 0
    assert dense["6"]["hits"] == 21
    assert dense["20"]["hits"] == 26
    assert dense["20"]["rate"] > dense["6"]["rate"]
    assert dense["20"]["rate"] > hybrid["20"]["rate"]
    assert inputs["dataset_sha256"] == _sha256(BASE / "adjudicated_items.jsonl")
    assert inputs["phase_a_records_sha256"] == _sha256(RESULTS / "calibration_phase_a.jsonl")
    assert inputs["corpus_sha256"] == _sha256(ROOT / "corpus" / "processed" / "chunks.jsonl")
