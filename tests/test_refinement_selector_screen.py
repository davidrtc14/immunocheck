from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_published_mmr_screen_is_bound_and_did_not_use_llm_or_holdout() -> None:
    results = ROOT / "evaluation" / "results" / "refinement_v2"
    calibration = ROOT / "evaluation" / "refinement_v2" / "calibration"
    report_path = results / "mmr_selector_screen.json"
    markdown_path = results / "MMR_SELECTOR_SCREEN.md"
    report = json.loads(report_path.read_text("utf-8"))
    manifest = json.loads((calibration / "manifest.json").read_text("utf-8"))
    receipt = manifest["mmr_selector_screen"]

    assert report["llm_calls"] == 0
    assert report["v1_test_items_loaded"] == report["holdout_v2_items_loaded"] == 0
    assert report["eligible_for_end_to_end"] is False
    assert sum(gate["passed"] for gate in report["gates"].values()) == 1
    assert report["systems"]["dense_top6"]["hits"] == 21
    assert report["systems"]["dense20_mmr6"]["hits"] == 12
    assert receipt["candidate_promoted"] is receipt["eligible_for_end_to_end"] is False
    assert receipt["report_sha256"] == _sha256(report_path)
    assert receipt["markdown_sha256"] == _sha256(markdown_path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
