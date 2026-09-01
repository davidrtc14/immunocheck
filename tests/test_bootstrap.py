from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from immunocheck import bootstrap
from immunocheck.domain.models import ExtractedClaim
from immunocheck.retrieval.dense import DenseIndex
from immunocheck.retrieval.rrf import HybridRetriever


class FakeEmbedder:
    dimension = 2

    def encode(self, texts):
        return np.asarray([[1.0, 0.0] for _ in texts], dtype=np.float32)


def write_corpus(path: Path) -> None:
    chunks = (
        {
            "chunk_id": "doc:p1:c1",
            "text": "A vacina usa adjuvante de alumínio.",
            "source": "Fonte oficial",
            "document_title": "Manual",
            "url": "https://example.gov.br/manual.pdf",
            "publication_date": "2026-01-01",
            "page_start": 1,
        },
        {
            "chunk_id": "doc:p2:c1",
            "text": "O calendário recomenda vacinação infantil.",
            "source": "Fonte oficial",
            "document_title": "Manual",
            "url": "https://example.gov.br/manual.pdf",
            "publication_date": "2026-01-01",
            "page_start": 2,
        },
    )
    path.write_text(
        "".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks),
        encoding="utf-8",
    )


def test_builds_hybrid_retriever_as_online_default(tmp_path: Path, monkeypatch) -> None:
    corpus_path = tmp_path / "chunks.jsonl"
    write_corpus(corpus_path)

    def fake_load_dense_index(*, evidence, **kwargs):
        del kwargs
        return DenseIndex(evidence, np.eye(2, dtype=np.float32)), object()

    monkeypatch.setattr(bootstrap, "load_dense_index", fake_load_dense_index)
    monkeypatch.setattr(bootstrap, "SentenceTransformerEmbedder", lambda **kwargs: FakeEmbedder())

    retriever = bootstrap._build_retriever(
        corpus_path=corpus_path,
        top_k=2,
        retrieval_mode="hybrid",
    )

    assert isinstance(retriever, HybridRetriever)
    assert len(retriever.retrieve(ExtractedClaim("vacina alumínio", 0.9))) == 2


def test_bm25_mode_remains_available_for_ablation(tmp_path: Path) -> None:
    corpus_path = tmp_path / "chunks.jsonl"
    write_corpus(corpus_path)

    retriever = bootstrap._build_retriever(
        corpus_path=corpus_path,
        top_k=1,
        retrieval_mode="bm25",
    )

    assert retriever.retrieve(ExtractedClaim("calendário infantil", 0.9))[0].page == 2


def test_rejects_unknown_retrieval_mode(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="RETRIEVAL_MODE"):
        bootstrap._build_retriever(
            corpus_path=tmp_path / "missing.jsonl",
            top_k=1,
            retrieval_mode="unknown",
        )
