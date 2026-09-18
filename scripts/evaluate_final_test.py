"""Executa uma única configuração congelada nos 64 itens de teste autorizados."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.ports import ClaimExtractor, FaithfulnessVerifier
from immunocheck.application.text_components import (
    GuardedFaithfulnessVerifier,
    LLMClaimExtractor,
    LLMFaithfulnessVerifier,
    LLMVerdictGenerator,
    ModelOutputError,
    TextNormalizer,
)
from immunocheck.domain.models import (
    ContentKind,
    ContentSubmission,
    ExtractedClaim,
    FactCheckResult,
    VerificationReport,
)
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.development_end_to_end import load_checkpoint, sha256_file
from immunocheck.evaluation.final_test import (
    FINAL_TEST_BOOTSTRAP_RESAMPLES,
    FINAL_TEST_BOOTSTRAP_SEED,
    load_frozen_test_items,
    summarize_final_test,
    validate_final_test_checkpoint,
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
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_CHECKPOINT = REPOSITORY / "evaluation/results/test/final_test_records.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/test/final_test.json"
GENERATOR_OUTPUT_DEPTH = 6


@dataclass(slots=True)
class RecordingClaimExtractor:
    delegate: ClaimExtractor
    last_claim: ExtractedClaim | None = None
    latency_ms: float = 0.0

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        started = time.perf_counter()
        try:
            self.last_claim = self.delegate.extract(normalized_text)
            return self.last_claim
        finally:
            self.latency_ms = (time.perf_counter() - started) * 1000


@dataclass(slots=True)
class RecordingVerifier:
    delegate: FaithfulnessVerifier
    reports: list[VerificationReport] = field(default_factory=list)

    def verify(self, claim, draft, evidence: Sequence) -> VerificationReport:
        report = self.delegate.verify(claim, draft, evidence)
        self.reports.append(report)
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação definitiva no teste congelado.")
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    candidate_commit = _validate_candidate_commit(args.candidate_commit)
    if args.output.exists():
        parser.error("Resultado final já existe; o teste congelado não pode ser reexecutado.")

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_test_items(BENCHMARK_ROOT)
    checkpoint = load_checkpoint(args.checkpoint)
    validate_final_test_checkpoint(checkpoint, items)
    if len(checkpoint) < len(items):
        pipeline, extractor, verifier = _build_pipeline(args.model)
        for index, item in enumerate(items[len(checkpoint) :], start=len(checkpoint) + 1):
            extractor.last_claim = None
            extractor.latency_ms = 0.0
            verifier.reports.clear()
            record = _evaluate_item(item, pipeline, extractor, verifier)
            _append_record(args.checkpoint, record)
            print(
                f"[{index}/{len(items)}] {item.item_id}: {record['result']['verdict']}",
                flush=True,
            )

    records = load_checkpoint(args.checkpoint)
    validate_final_test_checkpoint(records, items)
    summary = summarize_final_test(
        records,
        items,
        bootstrap_resamples=FINAL_TEST_BOOTSTRAP_RESAMPLES,
        seed=FINAL_TEST_BOOTSTRAP_SEED,
    )
    report = {
        "schema_version": 1,
        "purpose": "single_final_evaluation_no_post_test_tuning",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
        "partition": "test",
        "test_items_loaded": len(items),
        "post_test_changes_allowed": False,
        "authorization": {
            "actor_code": "project_author",
            "orientador_confirmed_by_author": True,
            "record": "explicit_confirmation_in_project_thread_2026-09-18",
        },
        "candidate_commit": candidate_commit,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "configuration": {
            "retrieval": "bge_m3_dense",
            "top_k": GENERATOR_OUTPUT_DEPTH,
            "reranker": False,
            "claim_extractor": "v2_material_integrity_guard",
            "generator": "qwen3_8b_local",
            "faithfulness_auditor": "v2_restored",
        },
        "model": args.model,
        "ollama_base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "seed": 42,
        "checkpoint_path": str(args.checkpoint.relative_to(REPOSITORY)).replace("\\", "/"),
        "checkpoint_sha256": sha256_file(args.checkpoint),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Resultado final salvo em {args.output.relative_to(REPOSITORY)}")


def _build_pipeline(
    model: str,
) -> tuple[FactCheckPipeline, RecordingClaimExtractor, RecordingVerifier]:
    evidence = load_evidence_jsonl(CORPUS_PATH)
    dense_index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS_PATH,
        manifest_path=DENSE_MANIFEST_PATH,
        corpus_path=CORPUS_PATH,
    )
    embedder = SentenceTransformerEmbedder(
        cache_folder=MODEL_CACHE,
        device="cpu",
        local_files_only=True,
    )
    client = OllamaStructuredClient(model=model)
    extractor = RecordingClaimExtractor(LLMClaimExtractor(client))
    verifier = RecordingVerifier(GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)))
    pipeline = FactCheckPipeline(
        normalizer=TextNormalizer(),
        claim_extractor=extractor,
        retriever=DenseRetriever(embedder, dense_index, top_k=GENERATOR_OUTPUT_DEPTH),
        generator=LLMVerdictGenerator(client),
        verifier=verifier,
    )
    return pipeline, extractor, verifier


def _evaluate_item(item, pipeline, extractor, verifier) -> dict[str, object]:
    started = time.perf_counter()
    error = None
    try:
        result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=item.claim))
    except (
        CorpusLoadError,
        DenseIndexError,
        ModelOutputError,
        OllamaError,
        ValueError,
    ) as exc:
        error = f"{type(exc).__name__}: {exc}"
        result = FactCheckResult.insufficient("Falha técnica durante a avaliação final.")
    latency_ms = (time.perf_counter() - started) * 1000
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": {
            "claim": extractor.last_claim.text if extractor.last_claim else None,
            "confidence": extractor.last_claim.confidence if extractor.last_claim else None,
            "multiple_claims_detected": (
                extractor.last_claim.multiple_claims_detected if extractor.last_claim else None
            ),
            "latency_ms": extractor.latency_ms,
        },
        "result": {
            "verdict": result.verdict.value,
            "explanation": result.explanation,
            "claim": result.claim,
            "correct_fact": result.correct_fact,
            "omitted_or_distorted": result.omitted_or_distorted,
            "source_ids": [source.chunk_id for source in result.sources],
            "multiple_claims_detected": result.multiple_claims_detected,
            "latency_ms": latency_ms,
            "technical_error": error,
            "auditor_invoked": bool(verifier.reports),
            "auditor_approved": verifier.reports[-1].all_supported if verifier.reports else None,
        },
    }


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


def _validate_candidate_commit(value: str) -> str:
    requested = value.strip().lower()
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Não foi possível validar o commit candidato.") from exc
    current = completed.stdout.strip().lower()
    if requested != current:
        raise SystemExit(f"Commit candidato divergente: esperado {requested}, atual {current}.")
    return current


if __name__ == "__main__":
    main()
