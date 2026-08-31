from __future__ import annotations

import csv
from pathlib import Path

from immunocheck.evaluation.retrieval import load_retrieval_judgments
from immunocheck.retrieval.bm25 import BM25Index
from immunocheck.retrieval.dense import (
    DenseIndex,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

PROJECT_ROOT = Path(__file__).parents[1]
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
JUDGMENTS_PATH = PROJECT_ROOT / "evaluation" / "retrieval" / "pilot_judgments.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "artifacts" / "retrieval_annotation_candidates.csv"
MODEL_CACHE = PROJECT_ROOT / "models"
CANDIDATE_DEPTH = 20


def main() -> None:
    evidence = load_evidence_jsonl(CORPUS_PATH)
    judgments = load_retrieval_judgments(
        JUDGMENTS_PATH,
        valid_chunk_ids={item.chunk_id for item in evidence},
    )
    dense_index, _ = load_dense_index(
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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=(
                "query_id",
                "query",
                "chunk_id",
                "source",
                "document_title",
                "page",
                "bm25_rank",
                "dense_rank",
                "hybrid_rank",
                "relevant",
                "annotation_notes",
                "text",
            ),
        )
        writer.writeheader()
        for judgment in judgments:
            _write_query_candidates(
                writer, judgment.query_id, judgment.query, bm25_index, dense_index, embedder
            )

    print(f"Planilha de anotação gerada em: {OUTPUT_PATH}")
    print(
        "Os rankings são apenas candidatos. Leia as fontes e preencha o gabarito humano "
        "antes de executar as métricas."
    )


def _write_query_candidates(
    writer: csv.DictWriter,
    query_id: str,
    query: str,
    bm25_index: BM25Index,
    dense_index: DenseIndex,
    embedder: SentenceTransformerEmbedder,
) -> None:
    bm25 = bm25_index.search(query, top_k=CANDIDATE_DEPTH)
    dense = dense_index.search(embedder.encode((query,)), top_k=CANDIDATE_DEPTH)
    hybrid = reciprocal_rank_fusion(
        (bm25, dense),
        top_k=CANDIDATE_DEPTH,
        rank_constant=60,
    )
    rankings = (bm25, dense, hybrid)
    rank_maps = tuple(
        {item.chunk_id: rank for rank, item in enumerate(ranking, start=1)} for ranking in rankings
    )
    candidates = {item.chunk_id: item for ranking in rankings for item in ranking}
    ordered = sorted(
        candidates.values(),
        key=lambda item: (
            min(rank_map.get(item.chunk_id, CANDIDATE_DEPTH + 1) for rank_map in rank_maps),
            item.chunk_id,
        ),
    )
    for item in ordered:
        writer.writerow(
            {
                "query_id": query_id,
                "query": query,
                "chunk_id": item.chunk_id,
                "source": item.source_name,
                "document_title": item.document_title,
                "page": item.page,
                "bm25_rank": rank_maps[0].get(item.chunk_id, ""),
                "dense_rank": rank_maps[1].get(item.chunk_id, ""),
                "hybrid_rank": rank_maps[2].get(item.chunk_id, ""),
                "relevant": "",
                "annotation_notes": "",
                "text": item.text,
            }
        )


if __name__ == "__main__":
    main()
