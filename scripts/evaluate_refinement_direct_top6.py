"""Avalia decisão direta em quatro classes reutilizando extração e top 6 da fase A."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from datetime import UTC, datetime
from pathlib import Path

from evaluate_refinement_calibration import (
    AlwaysSupportedVerifier,
    _append,
    _run_condition,
    _serialize,
)

from immunocheck.application.text_components import LLMVerdictGenerator
from immunocheck.domain.models import ExtractedClaim
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    REFINEMENT_CONDITIONS,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)
from immunocheck.infrastructure.ollama import OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v2/calibration/manifest.json"
PROTOCOL = ROOT / "evaluation/REFINEMENT_V2_PROTOCOL.md"
PLAN = ROOT / "evaluation/refinement_v2/DIRECT_TOP6_PLAN.md"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
PHASE_A_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
PHASE_A_REPORT = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.json"
TOP20_REPORT = ROOT / "evaluation/results/refinement_v2/calibration_top20.json"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/calibration_direct_top6.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v2/calibration_direct_top6.json"
DIRECT_CONDITIONS = (REFINEMENT_CONDITIONS[0], "v2_direct_dense_top6_no_auditor")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório direto top 6 já existe; não sobrescrever.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "mmr_selector_screen_failed_gates":
        parser.error("A triagem anterior não está no estado esperado.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    phase_a = load_refinement_checkpoint(PHASE_A_CHECKPOINT)
    validate_refinement_checkpoint(phase_a, items)
    if len(phase_a) != len(items):
        parser.error("O checkpoint completo da fase A é obrigatório.")
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items, conditions=DIRECT_CONDITIONS)

    if len(checkpoint) < len(items):
        client = OllamaStructuredClient(model=args.model)
        generator = LLMVerdictGenerator(client)
        evidence_by_id = {item.chunk_id: item for item in load_evidence_jsonl(CORPUS)}
        for index, (item, prior) in enumerate(
            zip(items[len(checkpoint) :], phase_a[len(checkpoint) :], strict=True),
            start=len(checkpoint) + 1,
        ):
            record = _evaluate_item(item, prior, evidence_by_id, generator)
            _append(args.checkpoint, record)
            print(
                f"[{index}/{len(items)}] {item.item_id}: "
                f"{DIRECT_CONDITIONS[1]}={record['conditions'][DIRECT_CONDITIONS[1]]['verdict']}",
                flush=True,
            )

    records = load_refinement_checkpoint(args.checkpoint)
    summary = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=REFINEMENT_BOOTSTRAP_RESAMPLES,
        seed=REFINEMENT_BOOTSTRAP_SEED,
        conditions=DIRECT_CONDITIONS,
    )
    phase_a_report = json.loads(PHASE_A_REPORT.read_text("utf-8"))
    top20_report = json.loads(TOP20_REPORT.read_text("utf-8"))
    candidate_f1 = summary["systems"][DIRECT_CONDITIONS[1]]["macro_f1"]
    report = {
        "schema_version": 1,
        "experiment": "refinement_v2_direct_dense_top6_no_auditor",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol_sha256": _sha256(PROTOCOL),
        "plan_sha256": _sha256(PLAN),
        "dataset_sha256": _sha256(DATASET),
        "phase_a_checkpoint_sha256": _sha256(PHASE_A_CHECKPOINT),
        "partition": "calibration_development_only",
        "v1_test_items_loaded": 0,
        "holdout_v2_items_loaded": 0,
        "model": args.model,
        "ollama_base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "seed": 42,
        "extraction": "reused_from_phase_a_without_new_llm_call",
        "retrieval": "reused_phase_a_bge_m3_dense_top_6",
        "single_changed_component_from_baseline": "remove_faithfulness_auditor",
        "conditions": list(DIRECT_CONDITIONS),
        "factual_auditor_executed": False,
        "descriptive_candidate_macro_f1": {
            "separated_top6": phase_a_report["summary"]["systems"][REFINEMENT_CONDITIONS[1]][
                "macro_f1"
            ],
            "separated_top20": top20_report["summary"]["systems"][
                "v2_separated_dense_top20_no_auditor"
            ]["macro_f1"],
            "direct_top6": candidate_f1,
        },
        "checkpoint_sha256": _sha256(args.checkpoint),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(ROOT)}")
    return 0


def _evaluate_item(item, prior, evidence_by_id, generator) -> dict[str, object]:
    extraction = prior["extraction"]
    claim = ExtractedClaim(
        text=str(extraction["claim"]),
        confidence=float(extraction["confidence"]),
        multiple_claims_detected=bool(extraction["multiple_claims_detected"]),
    )
    retrieved_ids = tuple(str(value) for value in extraction["retrieved_source_ids"])
    evidence = tuple(evidence_by_id[chunk_id] for chunk_id in retrieved_ids)
    result, inference_latency, error = _run_condition(
        item.claim,
        claim,
        evidence,
        generator,
        AlwaysSupportedVerifier(),
    )
    candidate = _serialize(
        result,
        float(extraction["latency_ms"]) + inference_latency,
        technical_error=error,
    )
    candidate["retrieved_source_ids"] = list(retrieved_ids)
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": dict(extraction),
        "conditions": {
            DIRECT_CONDITIONS[0]: dict(prior["conditions"][REFINEMENT_CONDITIONS[0]]),
            DIRECT_CONDITIONS[1]: candidate,
        },
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
