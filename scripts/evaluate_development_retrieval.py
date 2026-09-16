"""Compara BM25, BGE-M3 e RRF somente no desenvolvimento congelado."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.domain.models import Evidence
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
    RetrievalJudgment,
    evaluate_rankings,
)
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.dense import SentenceTransformerEmbedder, load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/development/retrieval_base.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieval no desenvolvimento congelado.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Resultado já existe; use --overwrite somente para reprodução declarada.")

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    judgments, families = build_development_retrieval_judgments(items)
    evidence = load_evidence_jsonl(CORPUS_PATH)
    dense_index, dense_manifest = load_dense_index(
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
    bm25 = BM25Index(evidence)
    embedder.encode((judgments[0].query,))
    systems: dict[str, Callable[[str], Sequence[Evidence]]] = {
        "bm25": lambda query: bm25.search(query, top_k=RETRIEVAL_RANKING_DEPTH),
        "dense_bge_m3": lambda query: dense_index.search(
            embedder.encode((query,)), top_k=RETRIEVAL_RANKING_DEPTH
        ),
        "hybrid_rrf": lambda query: reciprocal_rank_fusion(
            (
                bm25.search(query, top_k=RRF_INPUT_DEPTH),
                dense_index.search(embedder.encode((query,)), top_k=RRF_INPUT_DEPTH),
            ),
            top_k=RETRIEVAL_RANKING_DEPTH,
            rank_constant=RRF_RANK_CONSTANT,
        ),
    }
    results = {name: _evaluate_system(retrieve, judgments) for name, retrieve in systems.items()}
    rankings = {name: result["rankings"] for name, result in results.items()}
    report = {
        "schema_version": 1,
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
        "partition": "development",
        "test_queries_executed": 0,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "query_count": len(judgments),
        "excluded_insufficient_evidence_items": len(items) - len(judgments),
        "family_count": len(set(families.values())),
        "corpus_sha256": dense_manifest.corpus_sha256,
        "chunk_count": dense_manifest.chunk_count,
        "embedding_model": dense_manifest.model_name,
        "embedding_revision": dense_manifest.model_revision,
        "embedding_device": "cpu",
        "ranking_depth": RETRIEVAL_RANKING_DEPTH,
        "fusion_input_depth": RRF_INPUT_DEPTH,
        "rrf_rank_constant": RRF_RANK_CONSTANT,
        "systems": results,
        "bootstrap": cluster_bootstrap_retrieval(
            judgments,
            rankings,
            families,
            resamples=RETRIEVAL_BOOTSTRAP_RESAMPLES,
            seed=RETRIEVAL_BOOTSTRAP_SEED,
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")
    for name, result in results.items():
        metrics = result["metrics"]
        latency = result["latency_ms"]
        print(
            f"{name}: Recall@5={metrics['recall_at_5']:.3f}; "
            f"Recall@10={metrics['recall_at_10']:.3f}; MRR={metrics['mrr']:.3f}; "
            f"nDCG@10={metrics['ndcg_at_10']:.3f}; "
            f"mediana={latency['median']:.2f} ms; P95={latency['p95']:.2f} ms"
        )


def _evaluate_system(
    retrieve: Callable[[str], Sequence[Evidence]],
    judgments: Sequence[RetrievalJudgment],
) -> dict[str, object]:
    rankings: dict[str, tuple[str, ...]] = {}
    latencies: list[float] = []
    for judgment in judgments:
        started = time.perf_counter()
        result = retrieve(judgment.query)
        latencies.append((time.perf_counter() - started) * 1000)
        rankings[judgment.query_id] = tuple(item.chunk_id for item in result)
    metrics = asdict(evaluate_rankings(judgments, rankings))
    metrics.pop("per_query")
    return {
        "metrics": metrics,
        "latency_ms": {
            "median": statistics.median(latencies),
            "p95": sorted(latencies)[math.ceil(0.95 * len(latencies)) - 1],
            "samples": len(latencies),
        },
        "rankings": rankings,
    }


if __name__ == "__main__":
    main()
