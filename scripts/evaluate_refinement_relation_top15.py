"""Avalia a candidata relacional v3 com os 15 primeiros resultados densos."""

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

from immunocheck.application.text_components import LLMRelationVerdictGenerator
from immunocheck.domain.models import ExtractedClaim
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)
from immunocheck.infrastructure.ollama import OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v2/calibration/manifest.json"
PLAN = ROOT / "evaluation/refinement_v3/RELATION_TOP15_PLAN.md"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
PHASE_A_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
TOP20_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/calibration_top20.jsonl"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_relation_top15.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v3/calibration_relation_top15.json"
CONDITIONS = ("v1_dense_with_auditor", "v3_relation_dense_top15_no_auditor")
TOP_K = 15


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório relacional top 15 já existe; não sobrescrever.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "relation_v3_experiment_pending":
        parser.error("O manifesto não autoriza a execução relacional v3.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    phase_a = load_refinement_checkpoint(PHASE_A_CHECKPOINT)
    top20 = load_refinement_checkpoint(TOP20_CHECKPOINT)
    validate_refinement_checkpoint(phase_a, items)
    validate_refinement_checkpoint(
        top20,
        items,
        conditions=("v1_dense_with_auditor", "v2_separated_dense_top20_no_auditor"),
    )
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items, conditions=CONDITIONS)
    if len(phase_a) != len(items) or len(top20) != len(items):
        parser.error("Os checkpoints completos da fase A e top 20 são obrigatórios.")

    if len(checkpoint) < len(items):
        generator = LLMRelationVerdictGenerator(OllamaStructuredClient(model=args.model))
        evidence_by_id = {item.chunk_id: item for item in load_evidence_jsonl(CORPUS)}
        pending = zip(
            items[len(checkpoint) :],
            phase_a[len(checkpoint) :],
            top20[len(checkpoint) :],
            strict=True,
        )
        for index, (item, baseline, wide) in enumerate(pending, start=len(checkpoint) + 1):
            record = _evaluate_item(item, baseline, wide, evidence_by_id, generator)
            _append(args.checkpoint, record)
            verdict = record["conditions"][CONDITIONS[1]]["verdict"]
            print(f"[{index}/{len(items)}] {item.item_id}: {CONDITIONS[1]}={verdict}", flush=True)

    records = load_refinement_checkpoint(args.checkpoint)
    summary = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=REFINEMENT_BOOTSTRAP_RESAMPLES,
        seed=REFINEMENT_BOOTSTRAP_SEED,
        conditions=CONDITIONS,
    )
    report = {
        "schema_version": 1,
        "experiment": "refinement_v3_relation_dense_top15_no_auditor",
        "executed_at": datetime.now(UTC).isoformat(),
        "plan_sha256": _sha256(PLAN),
        "dataset_sha256": _sha256(DATASET),
        "phase_a_checkpoint_sha256": _sha256(PHASE_A_CHECKPOINT),
        "top20_checkpoint_sha256": _sha256(TOP20_CHECKPOINT),
        "partition": "reused_calibration_development_only_exploratory",
        "v1_test_items_loaded": 0,
        "holdout_v2_items_loaded": 0,
        "model": args.model,
        "temperature": 0,
        "seed": 42,
        "retrieval": "reused_bge_m3_dense_top_15_from_top20_checkpoint",
        "single_changed_component": "relation_aware_verdict_with_specific_event_guard",
        "conditions": list(CONDITIONS),
        "factual_auditor_executed": False,
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


def _evaluate_item(item, baseline, wide, evidence_by_id, generator) -> dict[str, object]:
    extraction = baseline["extraction"]
    claim = ExtractedClaim(
        text=str(extraction["claim"]),
        confidence=float(extraction["confidence"]),
        multiple_claims_detected=bool(extraction["multiple_claims_detected"]),
    )
    wide_condition = wide["conditions"]["v2_separated_dense_top20_no_auditor"]
    retrieved_ids = tuple(str(value) for value in wide_condition["retrieved_source_ids"][:TOP_K])
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
            CONDITIONS[0]: dict(baseline["conditions"][CONDITIONS[0]]),
            CONDITIONS[1]: candidate,
        },
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
