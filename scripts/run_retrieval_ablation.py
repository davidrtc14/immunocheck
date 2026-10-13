"""Ablação de retrieval (A2) sobre a calibração v4: mesma amostra, uma tabela, IC pareado por família.

Condições: denso top 15 (referência), BM25, híbrido RRF, denso top 30 + reranker e
híbrido + reranker. Usa somente a partição de calibração (`development`) do v4.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.evaluation.ablation import AblationCondition, render_ablation_table, run_ablation
from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items
from immunocheck.evaluation.retrieval import (
    RRF_INPUT_DEPTH,
    RRF_RANK_CONSTANT,
    AnnotationStatus,
    RetrievalJudgment,
)
from immunocheck.domain.models import Verdict
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.dense import SentenceTransformerEmbedder, load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl
from immunocheck.retrieval.reranker import (
    RERANK_MAX_LENGTH,
    SentenceTransformerCrossEncoderScorer,
    rerank_evidence,
)
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = REPOSITORY / "models"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/refinement_v4/results/retrieval_ablation_calibration.json"
DEPTH = 15
RERANK_POOL = 30


def main() -> None:
    parser = argparse.ArgumentParser(description="Ablação de retrieval na calibração v4.")
    parser.add_argument("--items", type=Path, default=ITEMS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Resultado já existe; use --overwrite somente para reprodução declarada.")

    items = [
        item
        for item in load_end_to_end_items(args.items, require_reviewed=True)
        if item.split is DatasetSplit.DEVELOPMENT and item.label is not Verdict.INSUFFICIENT_EVIDENCE
    ]
    judgments = [
        RetrievalJudgment(
            query_id=item.item_id,
            query=item.claim,
            status=AnnotationStatus.REVIEWED,
            relevant_chunk_ids=item.evidence_chunk_ids,
            reviewer=item.reviewer,
            reviewed_at=item.reviewed_at,
        )
        for item in items
    ]
    families = {item.item_id: item.claim_family or "" for item in items}

    evidence = load_evidence_jsonl(CORPUS_PATH)
    dense, _ = load_dense_index(
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

    rankings: dict[str, dict[str, tuple[str, ...]]] = {
        name: {}
        for name in ("dense_top15", "bm25_top15", "hybrid_rrf_top15", "dense30_rerank15", "hybrid_rerank15")
    }
    latency: dict[str, list[float]] = {name: [] for name in rankings}
    for judgment in judgments:
        started = time.perf_counter()
        semantic = dense.search(embedder.encode((judgment.query,)), top_k=RRF_INPUT_DEPTH)
        dense_seconds = time.perf_counter() - started
        rankings["dense_top15"][judgment.query_id] = tuple(c.chunk_id for c in semantic[:DEPTH])
        latency["dense_top15"].append(dense_seconds)

        started = time.perf_counter()
        lexical = bm25.search(judgment.query, top_k=RRF_INPUT_DEPTH)
        rankings["bm25_top15"][judgment.query_id] = tuple(c.chunk_id for c in lexical[:DEPTH])
        latency["bm25_top15"].append(time.perf_counter() - started)

        started = time.perf_counter()
        hybrid = reciprocal_rank_fusion(
            (lexical, semantic), top_k=RERANK_POOL, rank_constant=RRF_RANK_CONSTANT
        )
        rankings["hybrid_rrf_top15"][judgment.query_id] = tuple(c.chunk_id for c in hybrid[:DEPTH])
        latency["hybrid_rrf_top15"].append(dense_seconds + time.perf_counter() - started)

        started = time.perf_counter()
        reranked = rerank_evidence(judgment.query, semantic[:RERANK_POOL], scorer, top_k=DEPTH)
        rankings["dense30_rerank15"][judgment.query_id] = tuple(c.chunk_id for c in reranked)
        latency["dense30_rerank15"].append(dense_seconds + time.perf_counter() - started)

        started = time.perf_counter()
        reranked_hybrid = rerank_evidence(judgment.query, hybrid, scorer, top_k=DEPTH)
        rankings["hybrid_rerank15"][judgment.query_id] = tuple(
            c.chunk_id for c in reranked_hybrid
        )
        latency["hybrid_rerank15"].append(dense_seconds + time.perf_counter() - started)

    result = run_ablation(
        judgments,
        families,
        [AblationCondition(name, ranking) for name, ranking in rankings.items()],
        baseline="dense_top15",
    )
    result["partition"] = "calibration_v4_conclusive_items"
    result["holdout_items_loaded"] = False
    result["executed_at"] = datetime.now(UTC).isoformat()
    result["median_latency_seconds"] = {
        name: sorted(values)[len(values) // 2] for name, values in latency.items()
    }
    result["note"] = (
        "Consultas são a alegação crua. Gabarito de evidência curado pelo pesquisador com apoio "
        "de IA; a anotação consultou buscas sobre o corpus, o que pode favorecer sistemas "
        "lexicais ou densos."
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(render_ablation_table(result))


if __name__ == "__main__":
    main()
