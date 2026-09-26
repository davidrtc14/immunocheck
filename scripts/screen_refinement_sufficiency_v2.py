"""Tria o gate de suficiência v2 sem executar classificador ou auditor."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.application.text_components import (
    LLMAliasedEvidenceSufficiencyAssessor,
    ModelOutputError,
)
from immunocheck.domain.models import ExtractedClaim, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v2/calibration/manifest.json"
PLAN = ROOT / "evaluation/refinement_v2/SUFFICIENCY_V2_SCREEN_PLAN.md"
PHASE_A = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v2/sufficiency_v2_screen.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v2/sufficiency_v2_screen.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("A triagem do gate v2 já existe; não sobrescrever.")
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "direct_top6_failed_gates":
        parser.error("O experimento anterior não está no estado esperado.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    phase_a = load_refinement_checkpoint(PHASE_A)
    if len(phase_a) != len(items):
        parser.error("O checkpoint completo da fase A é obrigatório.")
    checkpoint = _load(args.checkpoint)
    _validate_prefix(checkpoint, items)
    evidence_by_id = {item.chunk_id: item for item in load_evidence_jsonl(CORPUS)}
    assessor = LLMAliasedEvidenceSufficiencyAssessor(
        OllamaStructuredClient(model=args.model)
    )

    for index, (item, prior) in enumerate(
        zip(items[len(checkpoint) :], phase_a[len(checkpoint) :], strict=True),
        start=len(checkpoint) + 1,
    ):
        extraction = prior["extraction"]
        claim = ExtractedClaim(
            text=str(extraction["claim"]),
            confidence=float(extraction["confidence"]),
            multiple_claims_detected=bool(extraction["multiple_claims_detected"]),
        )
        evidence = tuple(
            evidence_by_id[str(chunk_id)] for chunk_id in extraction["retrieved_source_ids"]
        )
        started = time.perf_counter()
        error = None
        assessment = None
        try:
            assessment = assessor.assess(claim, evidence)
        except (ModelOutputError, OllamaError, ValueError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        record = {
            "item_id": item.item_id,
            "claim_family": item.claim_family,
            "expected_label": item.label.value,
            "expected_sufficient": item.label is not Verdict.INSUFFICIENT_EVIDENCE,
            "predicted_sufficient": assessment.sufficient if assessment else False,
            "source_ids": list(assessment.source_ids) if assessment else [],
            "explanation": assessment.explanation if assessment else None,
            "latency_ms": (time.perf_counter() - started) * 1000,
            "technical_error": error,
        }
        _append(args.checkpoint, checkpoint, record)
        checkpoint = (*checkpoint, record)
        print(
            f"[{index}/{len(items)}] {item.item_id}: "
            f"sufficient={record['predicted_sufficient']}",
            flush=True,
        )

    report = _summarize(checkpoint, items)
    report.update(
        {
            "schema_version": 1,
            "experiment": "refinement_v2_sufficiency_gate_screen",
            "executed_at": datetime.now(UTC).isoformat(),
            "dataset_sha256": _sha256(DATASET),
            "phase_a_checkpoint_sha256": _sha256(PHASE_A),
            "plan_sha256": _sha256(PLAN),
            "checkpoint_sha256": _sha256(args.checkpoint),
            "model": args.model,
            "temperature": 0,
            "seed": 42,
            "classifier_calls": 0,
            "auditor_calls": 0,
            "v1_test_items_loaded": 0,
            "holdout_v2_items_loaded": 0,
        }
    )
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


def _summarize(records, items) -> dict[str, object]:
    item_by_id = {item.item_id: item for item in items}
    expected = [bool(record["expected_sufficient"]) for record in records]
    predicted = [bool(record["predicted_sufficient"]) for record in records]
    technical = [record["technical_error"] is not None for record in records]
    conclusive_indices = [index for index, value in enumerate(expected) if value]
    insufficient_indices = [index for index, value in enumerate(expected) if not value]
    misleading_indices = [
        index
        for index, record in enumerate(records)
        if record["expected_label"] == Verdict.MISLEADING.value
    ]
    selection_hits = sum(
        bool(
            set(item_by_id[str(records[index]["item_id"])].evidence_chunk_ids)
            & set(records[index]["source_ids"])
        )
        for index in conclusive_indices
    )
    sufficient_recall = sum(predicted[index] for index in conclusive_indices) / len(
        conclusive_indices
    )
    insufficient_recall = sum(not predicted[index] for index in insufficient_indices) / len(
        insufficient_indices
    )
    misleading_recall = sum(predicted[index] for index in misleading_indices) / len(
        misleading_indices
    )
    latency = _latency([float(record["latency_ms"]) for record in records])
    technical_rate = sum(technical) / len(records)
    gates = {
        "sufficient_recall": _gate(sufficient_recall, 0.70, "minimum"),
        "insufficient_recall": _gate(insufficient_recall, 0.67, "minimum"),
        "misleading_sufficient_recall": _gate(misleading_recall, 0.67, "minimum"),
        "annotated_selection_hit_rate": _gate(selection_hits / 36, 0.60, "minimum"),
        "technical_failure_rate": _gate(technical_rate, 0.02, "maximum"),
        "p95_seconds": _gate(float(latency["p95"]) / 1000, 8.0, "maximum"),
    }
    return {
        "item_count": len(records),
        "metrics": {
            "sufficient_recall": sufficient_recall,
            "insufficient_recall": insufficient_recall,
            "misleading_sufficient_recall": misleading_recall,
            "annotated_selection_hits": selection_hits,
            "annotated_selection_hit_rate": selection_hits / 36,
            "technical_failure_rate": technical_rate,
            "latency_ms": latency,
        },
        "gates": gates,
        "eligible_for_end_to_end": all(gate["passed"] for gate in gates.values()),
    }


def _load(path: Path) -> tuple[dict[str, object], ...]:
    if not path.exists():
        return ()
    return tuple(json.loads(line) for line in path.read_text("utf-8").splitlines() if line)


def _validate_prefix(records, items) -> None:
    if len(records) > len(items):
        raise ValueError("Checkpoint possui mais registros que a calibração.")
    for record, item in zip(records, items, strict=False):
        if record.get("item_id") != item.item_id or record.get("expected_label") != item.label.value:
            raise ValueError("Checkpoint não corresponde à calibração adjudicada.")


def _append(path: Path, existing, record) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        for value in (*existing, record):
            output.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def _latency(values: list[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "median": statistics.median(ordered),
        "p95": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "samples": len(ordered),
    }


def _gate(value: float, threshold: float, direction: str) -> dict[str, object]:
    return {
        "value": value,
        "threshold": threshold,
        "direction": direction,
        "passed": value >= threshold if direction == "minimum" else value <= threshold,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
