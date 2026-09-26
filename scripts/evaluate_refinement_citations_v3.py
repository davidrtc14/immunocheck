"""Avalia seleção dedicada de citações sem alterar os vereditos roteados v3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from evaluate_refinement_calibration import _append

from immunocheck.application.text_components import LLMCitationSelector, ModelOutputError
from immunocheck.domain.models import DraftVerdict, ExtractedClaim, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v2/calibration/manifest.json"
PLAN = ROOT / "evaluation/refinement_v3/CITATION_SELECTOR_PLAN.md"
ROUTED_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_routed.jsonl"
RELATION_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_relation_top15.jsonl"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/calibration_citations.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v3/calibration_citations.json"
BASELINE = "v1_dense_with_auditor"
ROUTED = "v3_routed_specialists_no_auditor"
CANDIDATE = "v3_routed_with_citation_selector"
RELATION = "v3_relation_dense_top15_no_auditor"
CONDITIONS = (BASELINE, CANDIDATE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório de citações v3 já existe; não sobrescrever.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "citation_selector_v3_experiment_pending":
        parser.error("O manifesto não autoriza a seleção de citações v3.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    routed = load_refinement_checkpoint(ROUTED_CHECKPOINT)
    relation = load_refinement_checkpoint(RELATION_CHECKPOINT)
    validate_refinement_checkpoint(routed, items, conditions=(BASELINE, ROUTED))
    validate_refinement_checkpoint(relation, items, conditions=(BASELINE, RELATION))
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items, conditions=CONDITIONS)
    if len(routed) != len(items) or len(relation) != len(items):
        parser.error("Os checkpoints roteado e relacional completos são obrigatórios.")

    if len(checkpoint) < len(items):
        selector = LLMCitationSelector(OllamaStructuredClient(model=args.model))
        evidence_by_id = {item.chunk_id: item for item in load_evidence_jsonl(CORPUS)}
        pending = zip(
            items[len(checkpoint) :],
            routed[len(checkpoint) :],
            relation[len(checkpoint) :],
            strict=True,
        )
        for index, (item, routed_record, relation_record) in enumerate(
            pending, start=len(checkpoint) + 1
        ):
            record = _evaluate_item(item, routed_record, relation_record, evidence_by_id, selector)
            _append(args.checkpoint, record)
            verdict = record["conditions"][CANDIDATE]["verdict"]
            selected = len(record["conditions"][CANDIDATE]["source_ids"])
            print(f"[{index}/{len(items)}] {item.item_id}: {verdict}, citações={selected}", flush=True)

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
        "experiment": "refinement_v3_routed_with_citation_selector",
        "executed_at": datetime.now(UTC).isoformat(),
        "plan_sha256": _sha256(PLAN),
        "dataset_sha256": _sha256(DATASET),
        "routed_checkpoint_sha256": _sha256(ROUTED_CHECKPOINT),
        "relation_checkpoint_sha256": _sha256(RELATION_CHECKPOINT),
        "partition": "reused_calibration_development_only_exploratory",
        "v1_test_items_loaded": 0,
        "holdout_items_loaded": 0,
        "model": args.model,
        "temperature": 0,
        "seed": 42,
        "verdict_changes_from_routed": _count_verdict_changes(records, routed),
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


def _evaluate_item(item, routed_record, relation_record, evidence_by_id, selector):
    extraction = routed_record["extraction"]
    claim = ExtractedClaim(
        text=str(extraction["claim"]),
        confidence=float(extraction["confidence"]),
        multiple_claims_detected=bool(extraction["multiple_claims_detected"]),
    )
    original = dict(routed_record["conditions"][ROUTED])
    candidate = dict(original)
    selection_latency = 0.0
    selection_error = None
    if original["verdict"] != Verdict.INSUFFICIENT_EVIDENCE.value:
        relation_condition = relation_record["conditions"][RELATION]
        retrieved_ids = tuple(str(value) for value in relation_condition["retrieved_source_ids"])
        evidence = tuple(evidence_by_id[chunk_id] for chunk_id in retrieved_ids)
        draft = DraftVerdict(
            verdict=Verdict(original["verdict"]),
            explanation=str(original["explanation"]),
            source_ids=tuple(str(value) for value in original["source_ids"]),
            correct_fact=original.get("correct_fact"),
            omitted_or_distorted=original.get("omitted_or_distorted"),
        )
        started = time.perf_counter()
        try:
            candidate["source_ids"] = list(selector.select(claim, draft, evidence))
        except (ModelOutputError, OllamaError, ValueError) as exc:
            selection_error = f"{type(exc).__name__}: {exc}"
        selection_latency = (time.perf_counter() - started) * 1000
        candidate["latency_ms"] = float(candidate["latency_ms"]) + selection_latency
        candidate["technical_error"] = selection_error
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": dict(extraction),
        "routing": dict(routed_record["routing"]),
        "citation_selection": {
            "called": original["verdict"] != Verdict.INSUFFICIENT_EVIDENCE.value,
            "latency_ms": selection_latency,
            "technical_error": selection_error,
        },
        "conditions": {
            BASELINE: dict(routed_record["conditions"][BASELINE]),
            CANDIDATE: candidate,
        },
    }


def _count_verdict_changes(records, routed) -> int:
    return sum(
        record["conditions"][CANDIDATE]["verdict"]
        != prior["conditions"][ROUTED]["verdict"]
        for record, prior in zip(records, routed, strict=True)
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
