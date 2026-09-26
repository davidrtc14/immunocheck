from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_published_sufficiency_v2_screen_is_bound_and_stopped_before_classifier() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v2"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    checkpoint_path = results / "sufficiency_v2_screen.jsonl"
    report_path = results / "sufficiency_v2_screen.json"
    report = json.loads(report_path.read_text("utf-8"))
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    receipt = manifest["sufficiency_v2_screen"]

    assert report["classifier_calls"] == report["auditor_calls"] == 0
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert report["metrics"]["sufficient_recall"] == 1.0
    assert report["metrics"]["insufficient_recall"] == 0.0
    assert report["eligible_for_end_to_end"] is False
    assert sum(gate["passed"] for gate in report["gates"].values()) == 4
    assert receipt["candidate_promoted"] is receipt["eligible_for_end_to_end"] is False
    assert receipt["checkpoint_sha256"] == _sha256(checkpoint_path)
    assert receipt["report_sha256"] == _sha256(report_path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
