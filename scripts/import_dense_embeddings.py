from __future__ import annotations

from pathlib import Path

from immunocheck.ingestion.corpus_versioning import (
    CorpusVersioningError,
    load_published_corpus,
)
from immunocheck.persistence.database import DatabaseConfigurationError, connect_database
from immunocheck.persistence.postgres import (
    CorpusRepositoryError,
    EmbeddingRecord,
    PostgresCorpusRepository,
)
from immunocheck.retrieval.dense import DenseIndexError, load_dense_index
from immunocheck.retrieval.pilot_corpus import CorpusLoadError, load_evidence_jsonl

PROJECT_ROOT = Path(__file__).parents[1]
PROCESSED_DIR = PROJECT_ROOT / "corpus" / "processed"
CORPUS_PATH = PROCESSED_DIR / "chunks.jsonl"
VECTORS_PATH = PROCESSED_DIR / "dense_bge_m3.npz"
DENSE_MANIFEST_PATH = PROCESSED_DIR / "dense_bge_m3.json"
CORPUS_MANIFEST_PATH = PROCESSED_DIR / "manifest.json"


def main() -> None:
    try:
        snapshot = load_published_corpus(
            manifest_path=CORPUS_MANIFEST_PATH,
            chunks_path=CORPUS_PATH,
        )
        evidence = load_evidence_jsonl(CORPUS_PATH)
        index, dense_manifest = load_dense_index(
            evidence=evidence,
            vectors_path=VECTORS_PATH,
            manifest_path=DENSE_MANIFEST_PATH,
            corpus_path=CORPUS_PATH,
        )
        records = tuple(
            EmbeddingRecord(chunk_id=chunk_id, values=vector)
            for chunk_id, vector in zip(index.chunk_ids, index.vectors, strict=True)
        )
        with connect_database() as connection:
            imported = PostgresCorpusRepository(connection).upsert_embeddings(
                corpus_version=str(snapshot.manifest["corpus_version"]),
                model_name=dense_manifest.model_name,
                model_revision=dense_manifest.model_revision,
                embeddings=records,
                normalized=dense_manifest.normalized,
            )
    except (
        CorpusVersioningError,
        CorpusLoadError,
        DenseIndexError,
        CorpusRepositoryError,
        DatabaseConfigurationError,
    ) as exc:
        print(f"FALHA: {exc}")
        raise SystemExit(1) from exc
    print(f"{imported} embedding(s) importado(s) para o PostgreSQL.")


if __name__ == "__main__":
    main()
