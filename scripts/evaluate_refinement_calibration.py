"""Executa baseline v1 e candidata separada nos 48 itens novos de calibração."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.text_components import (
    GuardedFaithfulnessVerifier,
    LLMClaimExtractor,
    LLMConclusiveVerdictGenerator,
    LLMEvidenceSufficiencyAssessor,
    LLMFaithfulnessVerifier,
    LLMVerdictGenerator,
    ModelOutputError,
    TextNormalizer,
)
from immunocheck.domain.models import (
    ContentKind,
    ContentSubmission,
    Evidence,
    ExtractedClaim,
    FactCheckResult,
    VerificationReport,
)
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
CORPUS = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_CHECKPOINT = REPOSITORY / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/refinement_v2/calibration_phase_a.json"
TOP_K = 6


@dataclass(slots=True)
class StaticClaimExtractor:
    claim: ExtractedClaim | None

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        del normalized_text
        return self.claim


@dataclass(slots=True)
class StaticRetriever:
    evidence: tuple[Evidence, ...]

    def retrieve(self, claim: ExtractedClaim) -> tuple[Evidence, ...]:
        del claim
        return self.evidence


@dataclass(slots=True)
class AlwaysSupportedVerifier:
    def verify(self, claim, draft, evidence) -> VerificationReport:
        del claim, draft, evidence
        return VerificationReport(all_supported=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibração fim a fim da candidata v2.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O relatório da fase A já existe; não sobrescrever a execução registrada.")

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "calibration_ready_experiment_pending":
        parser.error("A calibração humana ainda não está pronta para execução.")
    if _sha256(DATASET) != manifest["adjudicated_dataset_sha256"]:
        parser.error("O snapshot adjudicado não corresponde ao manifesto.")
    items = load_end_to_end_items(DATASET, require_reviewed=True)
    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_refinement_checkpoint(checkpoint, items)

    if len(checkpoint) < len(items):
        components = _build_components(args.model)
        for index, item in enumerate(items[len(checkpoint) :], start=len(checkpoint) + 1):
            record = _evaluate_item(item, components)
            _append(args.checkpoint, record)
            print(
                f"[{index}/{len(items)}] {item.item_id}: "
                + ", ".join(
                    f"{name}={record['conditions'][name]['verdict']}"
                    for name in REFINEMENT_CONDITIONS
                ),
                flush=True,
            )

    records = load_refinement_checkpoint(args.checkpoint)
    summary = summarize_refinement_records(
        records,
        items,
        bootstrap_resamples=REFINEMENT_BOOTSTRAP_RESAMPLES,
        seed=REFINEMENT_BOOTSTRAP_SEED,
    )
    report = {
        "schema_version": 1,
        "experiment": "refinement_v2_calibration_phase_a",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": str(PROTOCOL.relative_to(REPOSITORY)).replace("\\", "/"),
        "protocol_sha256": _sha256(PROTOCOL),
        "dataset": str(DATASET.relative_to(REPOSITORY)).replace("\\", "/"),
        "dataset_sha256": _sha256(DATASET),
        "partition": "calibration_development_only",
        "v1_test_items_loaded": 0,
        "holdout_v2_items_loaded": 0,
        "model": args.model,
        "ollama_base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "seed": 42,
        "retrieval": "bge_m3_dense_top_6",
        "conditions": list(REFINEMENT_CONDITIONS),
        "factual_auditor_executed": False,
        "factual_auditor_next_step": (
            "eligible_for_phase_b"
            if summary["factual_auditor_condition_eligible"]
            else "not_eligible_under_preregistered_gates"
        ),
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
        "extractor": LLMClaimExtractor(client),
        "retriever": DenseRetriever(
            SentenceTransformerEmbedder(
                cache_folder=MODEL_CACHE, device="cpu", local_files_only=True
            ),
            dense_index,
            top_k=TOP_K,
        ),
        "baseline_generator": LLMVerdictGenerator(client),
        "baseline_verifier": GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)),
        "candidate_assessor": LLMEvidenceSufficiencyAssessor(client),
        "candidate_generator": LLMConclusiveVerdictGenerator(client),
    }


def _evaluate_item(item, components: dict[str, object]) -> dict[str, object]:
    shared_started = time.perf_counter()
    error = None
    extracted = None
    evidence: tuple[Evidence, ...] = ()
    try:
        extracted = components["extractor"].extract(item.claim)  # type: ignore[attr-defined]
        if extracted is not None:
            evidence = tuple(components["retriever"].retrieve(extracted))  # type: ignore[attr-defined]
    except (CorpusLoadError, DenseIndexError, ModelOutputError, OllamaError, ValueError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    shared_latency = (time.perf_counter() - shared_started) * 1000
    extraction = {
        "claim": extracted.text if extracted else None,
        "confidence": extracted.confidence if extracted else None,
        "multiple_claims_detected": extracted.multiple_claims_detected if extracted else None,
        "retrieved_source_ids": [item.chunk_id for item in evidence],
        "latency_ms": shared_latency,
        "technical_error": error,
    }
    if extracted is None or error:
        fallback = FactCheckResult.insufficient(
            "Não foi possível preparar a alegação para avaliação local."
        )
        conditions = {
            name: _serialize(fallback, shared_latency, technical_error=error)
            for name in REFINEMENT_CONDITIONS
        }
    else:
        baseline = _run_condition(
            item.claim,
            extracted,
            evidence,
            components["baseline_generator"],
            components["baseline_verifier"],
        )
        candidate = _run_condition(
            item.claim,
            extracted,
            evidence,
            components["candidate_generator"],
            AlwaysSupportedVerifier(),
            assessor=components["candidate_assessor"],
        )
        conditions = {
            REFINEMENT_CONDITIONS[0]: _serialize(
                baseline[0], shared_latency + baseline[1], technical_error=baseline[2]
            ),
            REFINEMENT_CONDITIONS[1]: _serialize(
                candidate[0], shared_latency + candidate[1], technical_error=candidate[2]
            ),
        }
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": extraction,
        "conditions": conditions,
    }


def _run_condition(input_text, claim, evidence, generator, verifier, *, assessor=None):
    pipeline = FactCheckPipeline(
        normalizer=TextNormalizer(),
        claim_extractor=StaticClaimExtractor(claim),
        retriever=StaticRetriever(evidence),
        generator=generator,
        verifier=verifier,
        sufficiency_assessor=assessor,
    )
    started = time.perf_counter()
    error = None
    try:
        result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=input_text))
    except (CorpusLoadError, DenseIndexError, ModelOutputError, OllamaError, ValueError) as exc:
        error = f"{type(exc).__name__}: {exc}"
        result = FactCheckResult.insufficient("Falha técnica durante a avaliação local.")
    return result, (time.perf_counter() - started) * 1000, error


def _serialize(result: FactCheckResult, latency_ms: float, *, technical_error: str | None):
    return {
        "verdict": result.verdict.value,
        "explanation": result.explanation,
        "claim": result.claim,
        "correct_fact": result.correct_fact,
        "omitted_or_distorted": result.omitted_or_distorted,
        "source_ids": [source.chunk_id for source in result.sources],
        "multiple_claims_detected": result.multiple_claims_detected,
        "latency_ms": latency_ms,
        "technical_error": technical_error,
    }


def _append(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_refinement_checkpoint(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as output:
        for current in (*existing, record):
            output.write(json.dumps(current, ensure_ascii=False, separators=(",", ":")) + "\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    main()
