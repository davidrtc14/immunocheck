"""Executa as condições fim a fim pré-registradas somente no desenvolvimento."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.ports import FaithfulnessVerifier
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
    DraftVerdict,
    Evidence,
    ExtractedClaim,
    FactCheckResult,
    VerificationReport,
)
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.development_end_to_end import (
    END_TO_END_BOOTSTRAP_RESAMPLES,
    END_TO_END_BOOTSTRAP_SEED,
    END_TO_END_CONDITIONS,
    load_checkpoint,
    sha256_file,
    summarize_end_to_end_records,
    validate_checkpoint_prefix,
)
from immunocheck.evaluation.lexical_baseline import load_frozen_development_items
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.dense import (
    DenseIndexError,
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.pilot_corpus import (
    CorpusLoadError,
    PilotCorpusBM25Retriever,
    load_evidence_jsonl,
)
from immunocheck.retrieval.reranker import (
    RERANK_CANDIDATE_DEPTH,
    RerankerError,
    RerankingRetriever,
    SentenceTransformerCrossEncoderScorer,
)
from immunocheck.retrieval.rrf import HybridRetriever

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_CHECKPOINT = REPOSITORY / "evaluation/results/development/end_to_end_records.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/development/end_to_end.json"
RRF_INPUT_DEPTH = 60
RRF_RANK_CONSTANT = 60
GENERATOR_OUTPUT_DEPTH = 6


@dataclass(slots=True)
class StaticClaimExtractor:
    claim: ExtractedClaim | None

    def extract(self, normalized_text: str) -> ExtractedClaim | None:
        del normalized_text
        return self.claim


@dataclass(slots=True)
class StaticRetriever:
    evidence: tuple[Evidence, ...]

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        del claim
        return self.evidence


@dataclass(slots=True)
class ReplayGenerator:
    draft: DraftVerdict

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        del claim, evidence
        return self.draft


@dataclass(slots=True)
class CapturingRetriever:
    delegate: object
    last_evidence: tuple[Evidence, ...] | None = None

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        evidence = tuple(self.delegate.retrieve(claim))  # type: ignore[attr-defined]
        self.last_evidence = evidence
        return evidence


@dataclass(slots=True)
class CapturingGenerator:
    delegate: LLMVerdictGenerator
    last_draft: DraftVerdict | None = None

    def generate(self, claim: ExtractedClaim, evidence: Sequence[Evidence]) -> DraftVerdict:
        draft = self.delegate.generate(claim, evidence)
        self.last_draft = draft
        return draft


@dataclass(slots=True)
class AlwaysSupportedVerifier:
    def verify(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> VerificationReport:
        del claim, draft, evidence
        return VerificationReport(all_supported=True)


@dataclass(slots=True)
class RecordingVerifier:
    delegate: FaithfulnessVerifier
    reports: list[VerificationReport] = field(default_factory=list)

    def verify(
        self,
        claim: ExtractedClaim,
        draft: DraftVerdict,
        evidence: Sequence[Evidence],
    ) -> VerificationReport:
        report = self.delegate.verify(claim, draft, evidence)
        self.reports.append(report)
        return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação fim a fim no desenvolvimento.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error(
            "Resultado final já existe; a execução confirmatória de desenvolvimento é única."
        )

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    checkpoint = load_checkpoint(args.checkpoint)
    validate_checkpoint_prefix(checkpoint, items)
    if len(checkpoint) < len(items):
        components = _build_components(args.model)
        for index, item in enumerate(items[len(checkpoint) :], start=len(checkpoint) + 1):
            record = _evaluate_item(item, components)
            _append_record(args.checkpoint, record)
            print(
                f"[{index}/{len(items)}] {item.item_id}: "
                + ", ".join(
                    f"{name}={record['conditions'][name]['verdict']}"
                    for name in END_TO_END_CONDITIONS
                ),
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
    report = {
        "schema_version": 1,
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
        "partition": "development",
        "test_items_loaded": 0,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "model": args.model,
        "ollama_base_url": "http://127.0.0.1:11434",
        "temperature": 0,
        "seed": 42,
        "conditions": list(END_TO_END_CONDITIONS),
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
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")


def _build_components(model: str) -> dict[str, object]:
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
    bm25 = PilotCorpusBM25Retriever(evidence, top_k=GENERATOR_OUTPUT_DEPTH)
    dense = DenseRetriever(embedder, dense_index, top_k=GENERATOR_OUTPUT_DEPTH)
    hybrid_candidates = HybridRetriever(
        (
            PilotCorpusBM25Retriever(evidence, top_k=RRF_INPUT_DEPTH),
            DenseRetriever(embedder, dense_index, top_k=RRF_INPUT_DEPTH),
        ),
        top_k=RERANK_CANDIDATE_DEPTH,
        rank_constant=RRF_RANK_CONSTANT,
    )
    reranker = SentenceTransformerCrossEncoderScorer(
        cache_folder=MODEL_CACHE,
        device="cpu",
        batch_size=4,
        local_files_only=True,
    )
    client = OllamaStructuredClient(model=model)
    return {
        "claim_extractor": LLMClaimExtractor(client),
        "generator": LLMVerdictGenerator(client),
        "verifier": GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)),
        "bm25": bm25,
        "dense": dense,
        "reranked": RerankingRetriever(
            hybrid_candidates,
            reranker,
            top_k=GENERATOR_OUTPUT_DEPTH,
        ),
    }


def _evaluate_item(item, components: dict[str, object]) -> dict[str, object]:
    extraction_started = time.perf_counter()
    extraction_error = None
    try:
        extracted = components["claim_extractor"].extract(item.claim)  # type: ignore[attr-defined]
    except (
        CorpusLoadError,
        DenseIndexError,
        ModelOutputError,
        OllamaError,
        RerankerError,
        ValueError,
    ) as exc:
        extracted = None
        extraction_error = f"{type(exc).__name__}: {exc}"
    extraction_latency = (time.perf_counter() - extraction_started) * 1000
    extraction = {
        "claim": extracted.text if extracted else None,
        "confidence": extracted.confidence if extracted else None,
        "multiple_claims_detected": extracted.multiple_claims_detected if extracted else None,
        "latency_ms": extraction_latency,
        "technical_error": extraction_error,
    }
    if extracted is None:
        fallback = FactCheckResult.insufficient(
            "Não foi possível identificar uma alegação factual verificável."
        )
        reason = extraction_error
        conditions = {
            name: _serialize_condition(
                fallback,
                extraction_latency,
                technical_error=reason,
            )
            for name in END_TO_END_CONDITIONS
        }
    else:
        conditions = _evaluate_conditions(
            item.claim,
            extracted,
            extraction_latency,
            components,
        )
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": extraction,
        "conditions": conditions,
    }


def _evaluate_conditions(
    input_text: str,
    extracted: ExtractedClaim,
    extraction_latency: float,
    components: dict[str, object],
) -> dict[str, object]:
    bm25_result, bm25_latency, bm25_error = _run_pipeline(
        input_text,
        extracted,
        components["bm25"],
        components["generator"],
        AlwaysSupportedVerifier(),
    )
    dense_retriever = CapturingRetriever(components["dense"])
    dense_generator = CapturingGenerator(components["generator"])  # type: ignore[arg-type]
    dense_result, dense_latency, dense_error = _run_pipeline(
        input_text,
        extracted,
        dense_retriever,
        dense_generator,
        AlwaysSupportedVerifier(),
    )
    dense_auditor = RecordingVerifier(components["verifier"])  # type: ignore[arg-type]
    if dense_retriever.last_evidence is not None and dense_generator.last_draft is not None:
        dense_audited, audit_latency, audit_error = _run_pipeline(
            input_text,
            extracted,
            StaticRetriever(dense_retriever.last_evidence),
            ReplayGenerator(dense_generator.last_draft),
            dense_auditor,
        )
    else:
        dense_audited, audit_latency, audit_error = dense_result, 0.0, dense_error

    reranked_auditor = RecordingVerifier(components["verifier"])  # type: ignore[arg-type]
    reranked_result, reranked_latency, reranked_error = _run_pipeline(
        input_text,
        extracted,
        components["reranked"],
        components["generator"],
        reranked_auditor,
    )
    return {
        "bm25_no_auditor": _serialize_condition(
            bm25_result,
            extraction_latency + bm25_latency,
            technical_error=bm25_error,
        ),
        "dense_no_auditor": _serialize_condition(
            dense_result,
            extraction_latency + dense_latency,
            technical_error=dense_error,
        ),
        "dense_with_auditor": _serialize_condition(
            dense_audited,
            extraction_latency + dense_latency + audit_latency,
            technical_error=audit_error,
            reports=dense_auditor.reports,
        ),
        "hybrid_reranked_with_auditor": _serialize_condition(
            reranked_result,
            extraction_latency + reranked_latency,
            technical_error=reranked_error,
            reports=reranked_auditor.reports,
        ),
    }


def _run_pipeline(
    input_text: str,
    extracted: ExtractedClaim,
    retriever,
    generator,
    verifier,
) -> tuple[FactCheckResult, float, str | None]:
    pipeline = FactCheckPipeline(
        normalizer=TextNormalizer(),
        claim_extractor=StaticClaimExtractor(extracted),
        retriever=retriever,
        generator=generator,
        verifier=verifier,
    )
    started = time.perf_counter()
    error = None
    try:
        result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=input_text))
    except (
        CorpusLoadError,
        DenseIndexError,
        ModelOutputError,
        OllamaError,
        RerankerError,
        ValueError,
    ) as exc:
        error = f"{type(exc).__name__}: {exc}"
        result = FactCheckResult.insufficient("Falha técnica durante a avaliação local.")
    return result, (time.perf_counter() - started) * 1000, error


def _serialize_condition(
    result: FactCheckResult,
    latency_ms: float,
    *,
    technical_error: str | None,
    reports: Sequence[VerificationReport] = (),
) -> dict[str, object]:
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
        "auditor_invoked": bool(reports),
        "auditor_approved": reports[-1].all_supported if reports else None,
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


if __name__ == "__main__":
    main()
