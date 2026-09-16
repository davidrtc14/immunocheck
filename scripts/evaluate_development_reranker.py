"""Avalia o reranker pré-registrado somente no desenvolvimento."""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import statistics
import time
from collections.abc import Sequence
from ctypes import wintypes
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.development_retrieval import (
    RETRIEVAL_BOOTSTRAP_RESAMPLES,
    RETRIEVAL_BOOTSTRAP_SEED,
    build_development_retrieval_judgments,
    cluster_bootstrap_retrieval,
)
from immunocheck.evaluation.lexical_baseline import load_frozen_development_items
from immunocheck.evaluation.retrieval import (
    RETRIEVAL_RANKING_DEPTH,
    RRF_INPUT_DEPTH,
    RRF_RANK_CONSTANT,
    evaluate_rankings,
)
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.dense import SentenceTransformerEmbedder, load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl
from immunocheck.retrieval.reranker import (
    BGE_RERANKER_MODEL,
    BGE_RERANKER_REVISION,
    RERANK_CANDIDATE_DEPTH,
    RERANK_MAX_LENGTH,
    SentenceTransformerCrossEncoderScorer,
    rerank_evidence,
)
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/development/reranker.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Reranker no desenvolvimento congelado.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Resultado já existe; use --overwrite somente para reprodução declarada.")

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    judgments, families = build_development_retrieval_judgments(items)
    evidence = load_evidence_jsonl(CORPUS_PATH)
    dense, dense_manifest = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS_PATH,
        manifest_path=DENSE_MANIFEST_PATH,
        corpus_path=CORPUS_PATH,
    )
    embedder = SentenceTransformerEmbedder(
        cache_folder=MODEL_CACHE, device="cpu", local_files_only=True
    )
    scorer = SentenceTransformerCrossEncoderScorer(
        cache_folder=MODEL_CACHE,
        device="cpu",
        batch_size=4,
        max_length=RERANK_MAX_LENGTH,
        local_files_only=True,
    )
    bm25 = BM25Index(evidence)
    memory_before = _windows_memory_snapshot()
    warmup_started = time.perf_counter()
    first_vector = embedder.encode((judgments[0].query,))
    first_hybrid = reciprocal_rank_fusion(
        (
            bm25.search(judgments[0].query, top_k=RRF_INPUT_DEPTH),
            dense.search(first_vector, top_k=RRF_INPUT_DEPTH),
        ),
        top_k=RERANK_CANDIDATE_DEPTH,
        rank_constant=RRF_RANK_CONSTANT,
    )
    scorer.score(judgments[0].query, (first_hybrid[0].text,))
    warmup_seconds = time.perf_counter() - warmup_started
    memory_after_warmup = _windows_memory_snapshot()

    rankings: dict[str, dict[str, tuple[str, ...]]] = {
        name: {} for name in ("bm25", "dense_bge_m3", "hybrid_rrf", "hybrid_rrf_reranked")
    }
    retrieval_latencies: list[float] = []
    reranker_latencies: list[float] = []
    total_latencies: list[float] = []
    for judgment in judgments:
        total_started = time.perf_counter()
        retrieval_started = time.perf_counter()
        lexical = bm25.search(judgment.query, top_k=RRF_INPUT_DEPTH)
        semantic = dense.search(embedder.encode((judgment.query,)), top_k=RRF_INPUT_DEPTH)
        hybrid = reciprocal_rank_fusion(
            (lexical, semantic),
            top_k=RERANK_CANDIDATE_DEPTH,
            rank_constant=RRF_RANK_CONSTANT,
        )
        retrieval_latencies.append((time.perf_counter() - retrieval_started) * 1000)
        reranker_started = time.perf_counter()
        reranked = rerank_evidence(judgment.query, hybrid, scorer)
        reranker_latencies.append((time.perf_counter() - reranker_started) * 1000)
        total_latencies.append((time.perf_counter() - total_started) * 1000)
        rankings["bm25"][judgment.query_id] = tuple(
            item.chunk_id for item in lexical[:RETRIEVAL_RANKING_DEPTH]
        )
        rankings["dense_bge_m3"][judgment.query_id] = tuple(
            item.chunk_id for item in semantic[:RETRIEVAL_RANKING_DEPTH]
        )
        rankings["hybrid_rrf"][judgment.query_id] = tuple(
            item.chunk_id for item in hybrid[:RETRIEVAL_RANKING_DEPTH]
        )
        rankings["hybrid_rrf_reranked"][judgment.query_id] = tuple(
            item.chunk_id for item in reranked
        )
    memory_after_run = _windows_memory_snapshot()
    systems = {
        name: {
            "metrics": _metrics_without_per_query(judgments, system_rankings),
            "rankings": system_rankings,
        }
        for name, system_rankings in rankings.items()
    }
    systems["hybrid_rrf"]["latency_ms"] = _latency_summary(retrieval_latencies)
    systems["hybrid_rrf_reranked"]["reranker_latency_ms"] = _latency_summary(reranker_latencies)
    systems["hybrid_rrf_reranked"]["total_latency_ms"] = _latency_summary(total_latencies)
    bootstrap = cluster_bootstrap_retrieval(
        judgments,
        rankings,
        families,
        resamples=RETRIEVAL_BOOTSTRAP_RESAMPLES,
        seed=RETRIEVAL_BOOTSTRAP_SEED,
    )
    report = {
        "schema_version": 1,
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
        "partition": "development",
        "test_queries_executed": 0,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "query_count": len(judgments),
        "corpus_sha256": dense_manifest.corpus_sha256,
        "embedding_model": dense_manifest.model_name,
        "embedding_revision": dense_manifest.model_revision,
        "reranker_model": BGE_RERANKER_MODEL,
        "reranker_revision": BGE_RERANKER_REVISION,
        "device": "cpu",
        "candidate_depth": RERANK_CANDIDATE_DEPTH,
        "output_depth": RETRIEVAL_RANKING_DEPTH,
        "max_length": RERANK_MAX_LENGTH,
        "warmup_seconds": warmup_seconds,
        "process_memory": {
            "before_warmup": memory_before,
            "after_warmup": memory_after_warmup,
            "after_run": memory_after_run,
        },
        "systems": systems,
        "bootstrap": bootstrap,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")
    for name in ("hybrid_rrf", "hybrid_rrf_reranked", "dense_bge_m3"):
        metrics = systems[name]["metrics"]
        print(
            f"{name}: Recall@5={metrics['recall_at_5']:.3f}; "
            f"Recall@10={metrics['recall_at_10']:.3f}; MRR={metrics['mrr']:.3f}; "
            f"nDCG@10={metrics['ndcg_at_10']:.3f}"
        )
    print(
        "Reranker: mediana="
        f"{systems['hybrid_rrf_reranked']['reranker_latency_ms']['median']:.2f} ms; "
        f"P95={systems['hybrid_rrf_reranked']['reranker_latency_ms']['p95']:.2f} ms"
    )


def _metrics_without_per_query(judgments, rankings) -> dict[str, object]:
    metrics = asdict(evaluate_rankings(judgments, rankings))
    metrics.pop("per_query")
    return metrics


def _latency_summary(values: Sequence[float]) -> dict[str, float | int]:
    return {
        "median": statistics.median(values),
        "p95": sorted(values)[math.ceil(0.95 * len(values)) - 1],
        "samples": len(values),
    }


def _windows_memory_snapshot() -> dict[str, int] | None:
    if os.name != "nt":
        return None

    class ProcessMemoryCounters(ctypes.Structure):
        _fields_ = (
            ("cb", wintypes.DWORD),
            ("page_fault_count", wintypes.DWORD),
            ("peak_working_set_size", ctypes.c_size_t),
            ("working_set_size", ctypes.c_size_t),
            ("quota_peak_paged_pool_usage", ctypes.c_size_t),
            ("quota_paged_pool_usage", ctypes.c_size_t),
            ("quota_peak_non_paged_pool_usage", ctypes.c_size_t),
            ("quota_non_paged_pool_usage", ctypes.c_size_t),
            ("pagefile_usage", ctypes.c_size_t),
            ("peak_pagefile_usage", ctypes.c_size_t),
        )

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.restype = wintypes.HANDLE
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = (
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemoryCounters),
        wintypes.DWORD,
    )
    get_process_memory_info.restype = wintypes.BOOL
    process = get_current_process()
    succeeded = get_process_memory_info(process, ctypes.byref(counters), counters.cb)
    if not succeeded:
        return None
    return {
        "working_set_bytes": counters.working_set_size,
        "peak_working_set_bytes": counters.peak_working_set_size,
    }


if __name__ == "__main__":
    main()
