"""Avalia a candidata v2.1 alterando somente o retrieval denso para top 20."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from evaluate_refinement_calibration import (
    AlwaysSupportedVerifier,
    _append,
    _run_condition,
    _serialize,
)

from immunocheck.application.text_components import (
    LLMConclusiveVerdictGenerator,
    LLMEvidenceSufficiencyAssessor,
    ModelOutputError,
)
from immunocheck.domain.models import Evidence, ExtractedClaim, FactCheckResult
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import (
    REFINEMENT_BOOTSTRAP_RESAMPLES,
    REFINEMENT_BOOTSTRAP_SEED,
    REFINEMENT_CONDITIONS,
    load_refinement_checkpoint,
    summarize_refinement_records,
    validate_refinement_checkpoint,
)
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.dense import (
    DenseIndexError,
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.pilot_corpus import CorpusLoadError, load_evidence_jsonl

REPOSITORY = Path(__file__).resolve().parents[1]
DATASET = REPOSITORY / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
MANIFEST = REPOSITORY / "evaluation/refinement_v2/calibration/manifest.json"
PROTOCOL = REPOSITORY / "evaluation/REFINEMENT_V2_PROTOCOL.md"
PLAN = REPOSITORY / "evaluation/refinement_v2/CALIBRATION_TOP20_PLAN.md"
CORPUS = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
PHASE_A_CHECKPOINT = REPOSITORY / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
PHASE_A_REPORT = REPOSITORY / "evaluation/results/refinement_v2/calibration_phase_a.json"
DEFAULT_CHECKPOINT = REPOSITORY / "evaluation/results/refinement_v2/calibration_top20.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/refinement_v2/calibration_top20.json"
TOP_K = 20
TOP20_CONDITIONS = (
    REFINEMENT_CONDITIONS[0],
    "v2_separated_dense_top20_no_auditor",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibração da candidata v2.1 top 20.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório top 20 já existe; não sobrescrever a execução registrada.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "calibration_phase_a_failed_gates":
        parser.error("O diagnóstico da fase A não está no estado esperado.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    phase_a = load_refinement_checkpoint(PHASE_A_CHECKPOINT)
    validate_refinement_checkpoint(phase_a, items)
    if len(phase_a) != len(items):
        parser.error("O checkpoint completo da fase A é obrigatório.")
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items, conditions=TOP20_CONDITIONS)

    if len(checkpoint) < len(items):
        components = _build_components(args.model)
        for index, (item, prior) in enumerate(
            zip(items[len(checkpoint) :], phase_a[len(checkpoint) :], strict=True),
            start=len(checkpoint) + 1,
        ):
            record = _evaluate_item(item, prior, components)
            _append(args.checkpoint, record)
            print(
                f"[{index}/{len(items)}] {item.item_id}: "
                f"{TOP20_CONDITIONS[1]}={record['conditions'][TOP20_CONDITIONS[1]]['verdict']}",
                flush=True,
            )

    records = load_refinement_checkpoint(args.checkpoint)
    summary = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=REFINEMENT_BOOTSTRAP_RESAMPLES,
        seed=REFINEMENT_BOOTSTRAP_SEED,
        conditions=TOP20_CONDITIONS,
    )
    phase_a_report = json.loads(PHASE_A_REPORT.read_text("utf-8"))
    top6_macro_f1 = phase_a_report["summary"]["systems"][REFINEMENT_CONDITIONS[1]][
        "macro_f1"
    ]
    top20_macro_f1 = summary["systems"][TOP20_CONDITIONS[1]]["macro_f1"]
    report = {
        "schema_version": 1,
        "experiment": "refinement_v2_1_calibration_dense_top20",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": str(PROTOCOL.relative_to(REPOSITORY)).replace("\\", "/"),
        "protocol_sha256": _sha256(PROTOCOL),
        "plan": str(PLAN.relative_to(REPOSITORY)).replace("\\", "/"),
        "plan_sha256": _sha256(PLAN),
        "dataset": str(DATASET.relative_to(REPOSITORY)).replace("\\", "/"),
        "dataset_sha256": _sha256(DATASET),
        "phase_a_checkpoint_sha256": _sha256(PHASE_A_CHECKPOINT),
        "partition": "calibration_development_only",
        "v1_test_items_loaded": 0,
        "holdout_v2_items_loaded": 0,
        "model": args.model,
        "ollama_base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "seed": 42,
        "single_changed_component": "dense_retrieval_top_k_6_to_20",
        "retrieval": "bge_m3_dense_top_20",
        "extraction": "reused_from_phase_a_without_new_llm_call",
        "latency_method": (
            "phase_a_shared_extraction_plus_top6_retrieval_as_proxy_plus_new_inference; "
            "top20_retrieval_measured_separately"
        ),
        "conditions": list(TOP20_CONDITIONS),
        "factual_auditor_executed": False,
        "factual_auditor_next_step": (
            "eligible_for_phase_b"
            if summary["factual_auditor_condition_eligible"]
            else "not_eligible_under_preregistered_gates"
        ),
        "descriptive_comparison_with_top6": {
            "top6_candidate_macro_f1": top6_macro_f1,
            "top20_candidate_macro_f1": top20_macro_f1,
            "top20_minus_top6_macro_f1": top20_macro_f1 - top6_macro_f1,
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
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")


def _build_components(model: str) -> dict[str, object]:
    evidence = load_evidence_jsonl(CORPUS)
    dense_index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS,
        manifest_path=DENSE_MANIFEST,
        corpus_path=CORPUS,
    )
    client = OllamaStructuredClient(model=model)
    return {
        "retriever": DenseRetriever(
            SentenceTransformerEmbedder(
                cache_folder=MODEL_CACHE, device="cpu", local_files_only=True
            ),
            dense_index,
            top_k=TOP_K,
        ),
        "assessor": LLMEvidenceSufficiencyAssessor(client),
        "generator": LLMConclusiveVerdictGenerator(client),
    }


def _evaluate_item(item, prior, components: dict[str, object]) -> dict[str, object]:
    extraction = prior["extraction"]
    claim_text = extraction.get("claim")
    confidence = extraction.get("confidence")
    multiple = extraction.get("multiple_claims_detected")
    retrieval_started = time.perf_counter()
    error = None
    evidence: tuple[Evidence, ...] = ()
    claim = None
    try:
        if isinstance(claim_text, str) and isinstance(confidence, (int, float)):
            claim = ExtractedClaim(
                text=claim_text,
                confidence=float(confidence),
                multiple_claims_detected=bool(multiple),
            )
            evidence = tuple(components["retriever"].retrieve(claim))  # type: ignore[attr-defined]
        else:
            error = "PhaseAExtractionError: extração reutilizada ausente ou inválida"
    except (CorpusLoadError, DenseIndexError, ModelOutputError, OllamaError, ValueError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    retrieval_latency = (time.perf_counter() - retrieval_started) * 1000

    if claim is None or error:
        result = FactCheckResult.insufficient(
            "Não foi possível preparar a alegação para avaliação local.",
            claim=claim.text if claim else None,
        )
        condition = _serialize(
            result,
            float(extraction["latency_ms"]),
            technical_error=error,
        )
    else:
        result, inference_latency, condition_error = _run_condition(
            item.claim,
            claim,
            evidence,
            components["generator"],
            AlwaysSupportedVerifier(),
            assessor=components["assessor"],
        )
        condition = _serialize(
            result,
            float(extraction["latency_ms"]) + inference_latency,
            technical_error=condition_error,
        )
    condition["retrieved_source_ids"] = [evidence_item.chunk_id for evidence_item in evidence]
    condition["top20_retrieval_latency_ms"] = retrieval_latency
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": dict(extraction),
        "conditions": {
            TOP20_CONDITIONS[0]: dict(prior["conditions"][REFINEMENT_CONDITIONS[0]]),
            TOP20_CONDITIONS[1]: condition,
        },
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    main()
