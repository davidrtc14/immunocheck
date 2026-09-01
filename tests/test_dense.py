from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.dense import (
    BGE_M3_MODEL,
    BGE_M3_REVISION,
    DenseIndex,
    DenseIndexError,
    DenseRetriever,
    load_dense_index,
    load_reusable_dense_vectors,
    save_dense_index,
)

EVIDENCE = (
    Evidence("hpv", "Vacina HPV para adolescentes.", "MS", "HPV", "https://a"),
    Evidence("influenza", "Vacina contra influenza.", "MS", "Influenza", "https://b"),
    Evidence("covid", "Vacina contra covid-19.", "MS", "Covid", "https://c"),
)


class FakeEmbedder:
    dimension = 3

    def encode(self, texts):
        assert texts == ("vacinação HPV",)
        return np.asarray([[0.9, 0.1, 0.0]], dtype=np.float32)


def test_dense_index_ranks_by_cosine_similarity() -> None:
    vectors = np.eye(3, dtype=np.float32)
    index = DenseIndex(EVIDENCE, vectors)

    result = index.search(np.asarray([0.8, 0.2, 0.0], dtype=np.float32), top_k=2)

    assert [item.chunk_id for item in result] == ["hpv", "influenza"]
    assert result[0].retrieval_score > result[1].retrieval_score


def test_dense_retriever_embeds_claim() -> None:
    retriever = DenseRetriever(FakeEmbedder(), DenseIndex(EVIDENCE, np.eye(3)), top_k=1)

    result = retriever.retrieve(ExtractedClaim("vacinação HPV", 0.9))

    assert result[0].chunk_id == "hpv"


@pytest.mark.parametrize(
    "query",
    (
        np.asarray([0.0, 0.0, 0.0]),
        np.asarray([1.0, 0.0]),
        np.asarray([float("nan"), 0.0, 0.0]),
    ),
)
def test_dense_index_rejects_invalid_query(query: np.ndarray) -> None:
    index = DenseIndex(EVIDENCE, np.eye(3))

    with pytest.raises(DenseIndexError):
        index.search(query)


def test_dense_artifact_round_trip_and_corpus_hash_validation(tmp_path: Path) -> None:
    corpus = tmp_path / "chunks.jsonl"
    corpus.write_text('{"chunk_id":"hpv"}\n', encoding="utf-8")
    vectors_path = tmp_path / "dense.npz"
    manifest_path = tmp_path / "dense.json"
    index = DenseIndex(EVIDENCE, np.eye(3))
    save_dense_index(
        index=index,
        vectors_path=vectors_path,
        manifest_path=manifest_path,
        model_name=BGE_M3_MODEL,
        model_revision=BGE_M3_REVISION,
        sentence_transformers_version="test",
        corpus_path=corpus,
    )

    loaded, manifest = load_dense_index(
        evidence=EVIDENCE,
        vectors_path=vectors_path,
        manifest_path=manifest_path,
        corpus_path=corpus,
    )

    assert loaded.chunk_ids == ("hpv", "influenza", "covid")
    assert manifest.dimension == 3

    reusable, reusable_manifest = load_reusable_dense_vectors(
        vectors_path=vectors_path,
        manifest_path=manifest_path,
    )
    assert set(reusable) == {"hpv", "influenza", "covid"}
    assert reusable_manifest.corpus_sha256 == manifest.corpus_sha256
    assert np.array_equal(reusable["hpv"], np.asarray([1.0, 0.0, 0.0]))

    corpus.write_text('{"chunk_id":"changed"}\n', encoding="utf-8")
    with pytest.raises(DenseIndexError, match="corpus mudou"):
        load_dense_index(
            evidence=EVIDENCE,
            vectors_path=vectors_path,
            manifest_path=manifest_path,
            corpus_path=corpus,
        )


def test_loader_rejects_manifest_for_other_model(tmp_path: Path) -> None:
    corpus = tmp_path / "chunks.jsonl"
    corpus.write_text("corpus", encoding="utf-8")
    vectors_path = tmp_path / "dense.npz"
    manifest_path = tmp_path / "dense.json"
    with vectors_path.open("wb") as output:
        np.savez(output, vectors=np.eye(3), chunk_ids=np.asarray(["hpv", "influenza", "covid"]))
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "model_name": "other/model",
                "model_revision": "revision",
                "sentence_transformers_version": "test",
                "corpus_sha256": "unused",
                "chunk_count": 3,
                "dimension": 3,
                "normalized": True,
                "generated_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(DenseIndexError, match="outro modelo"):
        load_dense_index(
            evidence=EVIDENCE,
            vectors_path=vectors_path,
            manifest_path=manifest_path,
            corpus_path=corpus,
        )
