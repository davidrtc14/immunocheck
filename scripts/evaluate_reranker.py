from __future__ import annotations

import json
import math
import os
import statistics
import time
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.domain.models import Evidence
from immunocheck.evaluation.retrieval import (
    RETRIEVAL_RANKING_DEPTH,
    RRF_INPUT_DEPTH,
    RRF_RANK_CONSTANT,
    evaluate_rankings,
    load_retrieval_judgments,
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

PROJECT_ROOT = Path(__file__).parents[1]
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
JUDGMENTS_PATH = PROJECT_ROOT / "evaluation" / "retrieval" / "pilot_judgments.jsonl"
RUNS_DIR = PROJECT_ROOT / "runs"
MODEL_CACHE = PROJECT_ROOT / "models"


def main() -> None:
    memory_before_models = _windows_memory_snapshot()
    evidence = load_evidence_jsonl(CORPUS_PATH)
    judgments = load_retrieval_judgments(
        JUDGMENTS_PATH,
        valid_chunk_ids={item.chunk_id for item in evidence},
        require_reviewed=True,
    )
    dense_index, manifest = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS_PATH,
        manifest_path=MANIFEST_PATH,
        corpus_path=CORPUS_PATH,
    )
    embedder = SentenceTransformerEmbedder(
        cache_folder=MODEL_CACHE,
        device="cpu",
        local_files_only=True,
    )
    scorer = SentenceTransformerCrossEncoderScorer(
        cache_folder=MODEL_CACHE,
        device="cpu",
        batch_size=4,
        max_length=RERANK_MAX_LENGTH,
    )
    bm25_index = BM25Index(evidence)

    warmup_started_at = time.perf_counter()
    warmup_candidates = _hybrid_candidates(
        judgments[0].query,
        bm25_index,
        dense_index,
        embedder,
    )
    scorer.score(judgments[0].query, (warmup_candidates[0].text,))
    warmup_seconds = time.perf_counter() - warmup_started_at
    memory_after_warmup = _windows_memory_snapshot()

    base_rankings: dict[str, tuple[str, ...]] = {}
    reranked_rankings: dict[str, tuple[str, ...]] = {}
    retrieval_latencies_ms: list[float] = []
    reranker_latencies_ms: list[float] = []
    total_latencies_ms: list[float] = []
    for judgment in judgments:
        total_started_at = time.perf_counter()
        retrieval_started_at = time.perf_counter()
        candidates = _hybrid_candidates(judgment.query, bm25_index, dense_index, embedder)
        retrieval_latencies_ms.append((time.perf_counter() - retrieval_started_at) * 1000)
        base_rankings[judgment.query_id] = tuple(
            item.chunk_id for item in candidates[:RETRIEVAL_RANKING_DEPTH]
        )

        reranker_started_at = time.perf_counter()
        reranked = rerank_evidence(judgment.query, candidates, scorer)
        reranker_latencies_ms.append((time.perf_counter() - reranker_started_at) * 1000)
        total_latencies_ms.append((time.perf_counter() - total_started_at) * 1000)
        reranked_rankings[judgment.query_id] = tuple(item.chunk_id for item in reranked)

    memory_after_run = _windows_memory_snapshot()
    generated_at = datetime.now(UTC)
    report = {
        "schema_version": 1,
        "generated_at": generated_at.isoformat(),
        "dataset": str(JUDGMENTS_PATH.relative_to(PROJECT_ROOT)),
        "corpus_sha256": manifest.corpus_sha256,
        "chunk_count": manifest.chunk_count,
        "embedding_model": manifest.model_name,
        "embedding_revision": manifest.model_revision,
        "reranker_model": BGE_RERANKER_MODEL,
        "reranker_revision": BGE_RERANKER_REVISION,
        "reranker_device": "cpu",
        "reranker_max_length": RERANK_MAX_LENGTH,
        "reranker_candidate_depth": RERANK_CANDIDATE_DEPTH,
        "rrf_input_depth": RRF_INPUT_DEPTH,
        "rrf_rank_constant": RRF_RANK_CONSTANT,
        "warmup_seconds": warmup_seconds,
        "process_memory": {
            "before_models": memory_before_models,
            "after_warmup": memory_after_warmup,
            "after_run": memory_after_run,
        },
        "systems": {
            "hybrid_rrf": {
                "metrics": asdict(evaluate_rankings(judgments, base_rankings)),
                "rankings": base_rankings,
                "latency_ms": _latency_summary(retrieval_latencies_ms),
            },
            "hybrid_rrf_reranked": {
                "metrics": asdict(evaluate_rankings(judgments, reranked_rankings)),
                "rankings": reranked_rankings,
                "reranker_latency_ms": _latency_summary(reranker_latencies_ms),
                "total_latency_ms": _latency_summary(total_latencies_ms),
            },
        },
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RUNS_DIR / f"reranker_{generated_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Relatório salvo em {output_path}")
    print(f"Aquecimento e carga dos modelos: {warmup_seconds:.2f} s")
    for name, result in report["systems"].items():
        metrics = result["metrics"]
        latency = result.get("total_latency_ms", result.get("latency_ms"))
        print(
            f"{name}: Recall@5={metrics['recall_at_5']:.3f}; "
            f"Recall@10={metrics['recall_at_10']:.3f}; MRR={metrics['mrr']:.3f}; "
            f"nDCG@10={metrics['ndcg_at_10']:.3f}; "
            f"latência mediana={latency['median']:.2f} ms; P95={latency['p95']:.2f} ms"
        )


def _hybrid_candidates(
    query: str,
    bm25_index: BM25Index,
    dense_index,
    embedder: SentenceTransformerEmbedder,
) -> tuple[Evidence, ...]:
    return reciprocal_rank_fusion(
        (
            bm25_index.search(query, top_k=RRF_INPUT_DEPTH),
            dense_index.search(embedder.encode((query,)), top_k=RRF_INPUT_DEPTH),
        ),
        top_k=RERANK_CANDIDATE_DEPTH,
        rank_constant=RRF_RANK_CONSTANT,
    )


def _latency_summary(values: Sequence[float]) -> dict[str, float | int]:
    return {
        "median": statistics.median(values),
        "p95": _nearest_rank_percentile(values, 0.95),
        "samples": len(values),
    }


def _nearest_rank_percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("O percentil exige amostras.")
    ordered = sorted(values)
    return ordered[math.ceil(percentile * len(ordered)) - 1]


def _windows_memory_snapshot() -> dict[str, int] | None:
    if os.name != "nt":
        return None

    import ctypes
    from ctypes import wintypes

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
    succeeded = get_process_memory_info(
        process,
        ctypes.byref(counters),
        counters.cb,
    )
    if not succeeded:
        return None
    return {
        "working_set_bytes": counters.working_set_size,
        "peak_working_set_bytes": counters.peak_working_set_size,
    }


if __name__ == "__main__":
    main()
