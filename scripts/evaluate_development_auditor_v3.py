"""Calibra somente o auditor, reutilizando as saídas densas congeladas da v2."""

from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.application.text_components import (
    FACTUAL_VERIFICATION_SYSTEM_PROMPT_V3,
    GuardedFaithfulnessVerifier,
    LLMFaithfulnessVerifier,
    ModelOutputError,
)
from immunocheck.domain.models import Evidence, ExtractedClaim, Verdict
from immunocheck.evaluation.auditor_calibration import apply_audit_result, draft_from_condition
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.development_end_to_end import (
    END_TO_END_BOOTSTRAP_RESAMPLES,
    END_TO_END_BOOTSTRAP_SEED,
    compare_end_to_end_iterations,
    load_checkpoint,
    sha256_file,
    summarize_end_to_end_records,
    validate_checkpoint_prefix,
)
from immunocheck.evaluation.end_to_end import EndToEndDatasetError
from immunocheck.evaluation.lexical_baseline import load_frozen_development_items
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
BASELINE_CHECKPOINT = REPOSITORY / "evaluation/results/development/end_to_end_v2_records.jsonl"
BASELINE_REPORT = REPOSITORY / "evaluation/results/development/end_to_end_v2.json"
DEFAULT_CHECKPOINT = REPOSITORY / "evaluation/results/development/end_to_end_v3_records.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/development/end_to_end_v3.json"
CONDITION = "dense_with_auditor"
SOURCE_CONDITION = "dense_no_auditor"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibração isolada do auditor no desenvolvimento."
    )
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Resultado v3 já existe; a execução de calibração é única.")

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    baseline = load_checkpoint(BASELINE_CHECKPOINT)
    validate_checkpoint_prefix(baseline, items)
    if len(baseline) != len(items):
        raise EndToEndDatasetError("O checkpoint v2 precisa estar completo.")
    baseline_report = json.loads(BASELINE_REPORT.read_text("utf-8"))
    if baseline_report.get("test_items_loaded") != 0:
        raise EndToEndDatasetError("O relatório v2 não preserva o teste selado.")
    if baseline_report.get("checkpoint_sha256") != sha256_file(BASELINE_CHECKPOINT):
        raise EndToEndDatasetError("O checkpoint v2 diverge do relatório publicado.")

    checkpoint = load_checkpoint(args.checkpoint)
    validate_checkpoint_prefix(checkpoint, items)
    evidence_by_id = {item.chunk_id: item for item in load_evidence_jsonl(CORPUS_PATH)}
    verifier = GuardedFaithfulnessVerifier(
        LLMFaithfulnessVerifier(
            OllamaStructuredClient(model=args.model),
            system_prompt=FACTUAL_VERIFICATION_SYSTEM_PROMPT_V3,
            map_nonliteral_to_full_draft=True,
        )
    )
    for index in range(len(checkpoint), len(items)):
        record = _evaluate_record(baseline[index], evidence_by_id, verifier)
        _append_record(args.checkpoint, record)
        condition = record["conditions"][CONDITION]
        print(
            f"[{index + 1}/{len(items)}] {record['item_id']}: "
            f"{condition['verdict']} audit={condition['auditor_approved']}",
            flush=True,
        )

    records = load_checkpoint(args.checkpoint)
    validate_checkpoint_prefix(records, items)
    summary = summarize_end_to_end_records(
        records,
        items,
        bootstrap_resamples=END_TO_END_BOOTSTRAP_RESAMPLES,
        seed=END_TO_END_BOOTSTRAP_SEED,
    )
    comparison = compare_end_to_end_iterations(
        baseline,
        records,
        items,
        bootstrap_resamples=END_TO_END_BOOTSTRAP_RESAMPLES,
        seed=END_TO_END_BOOTSTRAP_SEED,
    )
    report = {
        "schema_version": 1,
        "development_iteration": 3,
        "single_changed_component": "faithfulness_auditor_objective",
        "execution_mode": "replay_v2_extraction_retrieval_and_generation",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
        "partition": "development",
        "test_items_loaded": 0,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "model": args.model,
        "temperature": 0,
        "seed": 42,
        "baseline_checkpoint_sha256": sha256_file(BASELINE_CHECKPOINT),
        "checkpoint_path": str(args.checkpoint.relative_to(REPOSITORY)).replace("\\", "/"),
        "checkpoint_sha256": sha256_file(args.checkpoint),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "summary": summary,
        "comparison_with_v2": comparison,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")


def _evaluate_record(
    baseline: dict[str, object],
    evidence_by_id: dict[str, Evidence],
    verifier: GuardedFaithfulnessVerifier,
) -> dict[str, object]:
    conditions = baseline.get("conditions")
    extraction = baseline.get("extraction")
    if not isinstance(conditions, dict) or not isinstance(extraction, dict):
        raise EndToEndDatasetError("Registro v2 incompleto.")
    source = conditions.get(SOURCE_CONDITION)
    claim_text = extraction.get("claim")
    if not isinstance(source, dict) or not isinstance(claim_text, str):
        raise EndToEndDatasetError("Saída densa ou alegação extraída ausente na v2.")

    draft = draft_from_condition(source)
    report = None
    error = None
    audit_latency = 0.0
    should_audit = bool(draft.source_ids) or draft.verdict is not Verdict.INSUFFICIENT_EVIDENCE
    if source.get("technical_error") is None and should_audit:
        try:
            evidence = tuple(evidence_by_id[source_id] for source_id in draft.source_ids)
            started = time.perf_counter()
            report = verifier.verify(ExtractedClaim(claim_text, 1.0), draft, evidence)
            audit_latency = (time.perf_counter() - started) * 1000
        except (KeyError, ModelOutputError, OllamaError, ValueError) as exc:
            audit_latency = (time.perf_counter() - started) * 1000 if "started" in locals() else 0.0
            error = f"{type(exc).__name__}: {exc}"

    candidate = apply_audit_result(
        source,
        report=report,
        audit_latency_ms=audit_latency,
        technical_error=error,
    )
    result = copy.deepcopy(baseline)
    result_conditions = result["conditions"]
    if not isinstance(result_conditions, dict):
        raise EndToEndDatasetError("Condições v2 inválidas.")
    result_conditions[CONDITION] = candidate
    return result


def _append_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_checkpoint(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        for current in (*existing, record):
            output.write(json.dumps(current, ensure_ascii=False, separators=(",", ":")) + "\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


if __name__ == "__main__":
    main()
