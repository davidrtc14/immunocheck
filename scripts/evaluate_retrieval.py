from __future__ import annotations

import json
import math
import statistics
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.domain.models import Evidence
from immunocheck.evaluation.retrieval import (
    RetrievalEvaluationError,
    RetrievalJudgment,
    evaluate_rankings,
    load_retrieval_judgments,
)
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.dense import SentenceTransformerEmbedder, load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

PROJECT_ROOT = Path(__file__).parents[1]
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
JUDGMENTS_PATH = PROJECT_ROOT / "evaluation" / "retrieval" / "pilot_judgments.jsonl"
RUNS_DIR = PROJECT_ROOT / "runs"
MODEL_CACHE = PROJECT_ROOT / "models"
RANKING_DEPTH = 10
FUSION_INPUT_DEPTH = 60


def main() -> None:
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
    bm25_index = BM25Index(evidence)

    embedder.encode((judgments[0].query,))
    systems: dict[str, Callable[[str], Sequence[Evidence]]] = {
        "bm25": lambda query: bm25_index.search(query, top_k=RANKING_DEPTH),
        "dense_bge_m3": lambda query: dense_index.search(
            embedder.encode((query,)), top_k=RANKING_DEPTH
        ),
        "hybrid_rrf": lambda query: reciprocal_rank_fusion(
            (
                bm25_index.search(query, top_k=FUSION_INPUT_DEPTH),
                dense_index.search(embedder.encode((query,)), top_k=FUSION_INPUT_DEPTH),
            ),
            top_k=RANKING_DEPTH,
            rank_constant=60,
        ),
    }

    results = {
        name: _evaluate_system(name, retrieve, judgments) for name, retrieve in systems.items()
    }
    generated_at = datetime.now(UTC)
    report = {
        "schema_version": 1,
        "generated_at": generated_at.isoformat(),
        "dataset": str(JUDGMENTS_PATH.relative_to(PROJECT_ROOT)),
        "corpus_sha256": manifest.corpus_sha256,
        "chunk_count": manifest.chunk_count,
        "embedding_model": manifest.model_name,
        "embedding_revision": manifest.model_revision,
        "ranking_depth": RANKING_DEPTH,
        "fusion_input_depth": FUSION_INPUT_DEPTH,
        "systems": results,
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RUNS_DIR / f"retrieval_{generated_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Relatório salvo em {output_path}")
    for name, result in results.items():
        metrics = result["metrics"]
        latency = result["latency_ms"]
        print(
            f"{name}: Recall@5={metrics['recall_at_5']:.3f}; "
            f"Recall@10={metrics['recall_at_10']:.3f}; MRR={metrics['mrr']:.3f}; "
            f"nDCG@10={metrics['ndcg_at_10']:.3f}; "
            f"latência mediana={latency['median']:.2f} ms; P95={latency['p95']:.2f} ms"
        )


def _evaluate_system(
    name: str,
    retrieve: Callable[[str], Sequence[Evidence]],
    judgments: Sequence[RetrievalJudgment],
) -> dict[str, object]:
    rankings: dict[str, tuple[str, ...]] = {}
    latencies_ms: list[float] = []
    for judgment in judgments:
        started_at = time.perf_counter()
        result = retrieve(judgment.query)
        latencies_ms.append((time.perf_counter() - started_at) * 1000)
        rankings[judgment.query_id] = tuple(item.chunk_id for item in result)

    metrics = evaluate_rankings(judgments, rankings)
    return {
        "name": name,
        "metrics": asdict(metrics),
        "latency_ms": {
            "median": statistics.median(latencies_ms),
            "p95": _nearest_rank_percentile(latencies_ms, 0.95),
            "samples": len(latencies_ms),
        },
        "rankings": rankings,
    }


def _nearest_rank_percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("O percentil exige amostras.")
    if not 0 < percentile <= 1:
        raise ValueError("O percentil deve estar no intervalo (0, 1].")
    ordered = sorted(values)
    rank = math.ceil(percentile * len(ordered))
    return ordered[rank - 1]


if __name__ == "__main__":
    try:
        main()
    except RetrievalEvaluationError as exc:
        raise SystemExit(f"Experimento não executado: {exc}") from exc
