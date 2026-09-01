from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import sentence_transformers

from immunocheck.retrieval.dense import (
    BGE_M3_MODEL,
    BGE_M3_REVISION,
    DenseIndex,
    SentenceTransformerEmbedder,
    load_reusable_dense_vectors,
    save_dense_index,
)
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

PROJECT_ROOT = Path(__file__).parents[1]
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
MODEL_CACHE = PROJECT_ROOT / "models"


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói o índice BGE-M3 local.")
    parser.add_argument(
        "--full-rebuild",
        action="store_true",
        help="ignora o artefato anterior e recalcula todos os vetores",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="usa somente pesos já presentes no cache local",
    )
    args = parser.parse_args()
    evidence = load_evidence_jsonl(CORPUS_PATH)
    reusable = {}
    if not args.full_rebuild and VECTORS_PATH.exists() and MANIFEST_PATH.exists():
        reusable, _ = load_reusable_dense_vectors(
            vectors_path=VECTORS_PATH,
            manifest_path=MANIFEST_PATH,
        )
    pending = tuple(item for item in evidence if item.chunk_id not in reusable)
    embedder = SentenceTransformerEmbedder(
        cache_folder=MODEL_CACHE,
        device="cpu",
        local_files_only=args.offline,
        show_progress_bar=True,
    )
    print(
        f"Índice incremental: {len(evidence) - len(pending)} vetor(es) reutilizado(s), "
        f"{len(pending)} a gerar em CPU."
    )
    started_at = time.perf_counter()
    generated = embedder.encode(tuple(item.text for item in pending))
    generated_by_id = {
        item.chunk_id: vector for item, vector in zip(pending, generated, strict=True)
    }
    vectors = np.vstack(
        tuple(
            reusable[item.chunk_id]
            if item.chunk_id in reusable
            else generated_by_id[item.chunk_id]
            for item in evidence
        )
    )
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
