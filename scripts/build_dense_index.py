from __future__ import annotations

import time
from pathlib import Path

import sentence_transformers

from immunocheck.retrieval.dense import (
    BGE_M3_MODEL,
    BGE_M3_REVISION,
    DenseIndex,
    SentenceTransformerEmbedder,
    save_dense_index,
)
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

PROJECT_ROOT = Path(__file__).parents[1]
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
MODEL_CACHE = PROJECT_ROOT / "models"


def main() -> None:
    evidence = load_evidence_jsonl(CORPUS_PATH)
    embedder = SentenceTransformerEmbedder(
        cache_folder=MODEL_CACHE,
        device="cpu",
        show_progress_bar=True,
    )
    print(f"Gerando embeddings BGE-M3 em CPU para {len(evidence)} trechos...")
    started_at = time.perf_counter()
    vectors = embedder.encode(tuple(item.text for item in evidence))
    index = DenseIndex(evidence, vectors)
    manifest = save_dense_index(
        index=index,
        vectors_path=VECTORS_PATH,
        manifest_path=MANIFEST_PATH,
        model_name=BGE_M3_MODEL,
        model_revision=BGE_M3_REVISION,
        sentence_transformers_version=sentence_transformers.__version__,
        corpus_path=CORPUS_PATH,
    )
    elapsed = time.perf_counter() - started_at
    print(
        f"Índice denso concluído: {manifest.chunk_count} trechos, "
        f"{manifest.dimension} dimensões, {elapsed:.2f} s."
    )
    print(f"Artefatos locais: {VECTORS_PATH.name} e {MANIFEST_PATH.name}")


if __name__ == "__main__":
    main()
