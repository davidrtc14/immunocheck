"""Avalia roteamento estrutural entre decisões direta, relacional e abstenção."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from evaluate_refinement_calibration import _append, _serialize

from immunocheck.application.text_components import LLMClaimRouteAnalyzer, ModelOutputError
from immunocheck.domain.models import ExtractedClaim, FactCheckResult
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v2/calibration/manifest.json"
PLAN = ROOT / "evaluation/refinement_v3/ROUTED_DECISION_PLAN.md"
DIRECT_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/calibration_direct_top6.jsonl"
RELATION_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_relation_top15.jsonl"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_routed.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v3/calibration_routed.json"
BASELINE = "v1_dense_with_auditor"
DIRECT = "v2_direct_dense_top6_no_auditor"
RELATION = "v3_relation_dense_top15_no_auditor"
CANDIDATE = "v3_routed_specialists_no_auditor"
CONDITIONS = (BASELINE, CANDIDATE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório roteado já existe; não sobrescrever.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "routed_v3_experiment_pending":
        parser.error("O manifesto não autoriza a execução roteada v3.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    direct = load_refinement_checkpoint(DIRECT_CHECKPOINT)
    relation = load_refinement_checkpoint(RELATION_CHECKPOINT)
    validate_refinement_checkpoint(direct, items, conditions=(BASELINE, DIRECT))
    validate_refinement_checkpoint(relation, items, conditions=(BASELINE, RELATION))
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items, conditions=CONDITIONS)
    if len(direct) != len(items) or len(relation) != len(items):
        parser.error("Os checkpoints completos dos dois especialistas são obrigatórios.")

    if len(checkpoint) < len(items):
        router = LLMClaimRouteAnalyzer(OllamaStructuredClient(model=args.model))
        pending = zip(
            items[len(checkpoint) :],
            direct[len(checkpoint) :],
            relation[len(checkpoint) :],
            strict=True,
        )
        for index, (item, direct_record, relation_record) in enumerate(
            pending, start=len(checkpoint) + 1
        ):
            record = _evaluate_item(item, direct_record, relation_record, router)
            _append(args.checkpoint, record)
            route = record["routing"]["route"]
            verdict = record["conditions"][CANDIDATE]["verdict"]
            print(f"[{index}/{len(items)}] {item.item_id}: {route} -> {verdict}", flush=True)

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
        "experiment": "refinement_v3_routed_specialists_no_auditor",
        "executed_at": datetime.now(UTC).isoformat(),
        "plan_sha256": _sha256(PLAN),
        "dataset_sha256": _sha256(DATASET),
        "direct_checkpoint_sha256": _sha256(DIRECT_CHECKPOINT),
        "relation_checkpoint_sha256": _sha256(RELATION_CHECKPOINT),
        "partition": "reused_calibration_development_only_exploratory",
        "v1_test_items_loaded": 0,
        "holdout_items_loaded": 0,
        "model": args.model,
        "temperature": 0,
        "seed": 42,
        "routing": {
            "GENERAL_SIMPLE": "direct_dense_top6",
            "PREMISE_CONCLUSION": "relation_dense_top15",
            "UNANCHORED_SPECIFIC_EVENT": "deterministic_abstention",
        },
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


def _evaluate_item(item, direct_record, relation_record, router) -> dict[str, object]:
    extraction = direct_record["extraction"]
    claim = ExtractedClaim(
        text=str(extraction["claim"]),
        confidence=float(extraction["confidence"]),
        multiple_claims_detected=bool(extraction["multiple_claims_detected"]),
    )
    started = time.perf_counter()
    error = None
    try:
        assessment = router.analyze(claim)
        route = assessment.route
        explanation = assessment.explanation
    except (ModelOutputError, OllamaError, ValueError) as exc:
        error = f"{type(exc).__name__}: {exc}"
        route = "ROUTING_FAILURE"
        explanation = "Não foi possível determinar com segurança a forma da alegação."
    routing_latency = (time.perf_counter() - started) * 1000

    if route == "GENERAL_SIMPLE":
        candidate = dict(direct_record["conditions"][DIRECT])
        candidate["latency_ms"] = float(candidate["latency_ms"]) + routing_latency
    elif route == "PREMISE_CONCLUSION":
        candidate = dict(relation_record["conditions"][RELATION])
        candidate["latency_ms"] = float(candidate["latency_ms"]) + routing_latency
    else:
        result = FactCheckResult.insufficient(
            explanation,
            claim=claim.text,
            multiple_claims_detected=claim.multiple_claims_detected,
        )
        candidate = _serialize(
            result,
            float(extraction["latency_ms"]) + routing_latency,
            technical_error=error,
        )
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": dict(extraction),
        "routing": {
            "route": route,
            "explanation": explanation,
            "latency_ms": routing_latency,
            "technical_error": error,
        },
        "conditions": {
            BASELINE: dict(direct_record["conditions"][BASELINE]),
            CANDIDATE: candidate,
        },
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
