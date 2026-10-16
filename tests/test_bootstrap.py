from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from immunocheck import bootstrap
from immunocheck.application.routed_pipeline import RoutedFactCheckPipeline
from immunocheck.application.text_components import (
    GuardedFaithfulnessVerifier,
    LLMConclusiveVerdictGenerator,
    LLMEvidenceSufficiencyAssessor,
    LLMVerdictGenerator,
)
from immunocheck.domain.models import ExtractedClaim
from immunocheck.retrieval.dense import DenseIndex, DenseRetriever
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


def test_builds_dense_retriever_as_online_default(tmp_path: Path, monkeypatch) -> None:
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
        retrieval_mode="dense",
    )

    assert isinstance(retriever, DenseRetriever)
    assert len(retriever.retrieve(ExtractedClaim("vacina alumínio", 0.9))) == 2


def test_hybrid_mode_remains_available_for_ablation(tmp_path: Path, monkeypatch) -> None:
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


def test_refinement_decision_components_are_separate_and_opt_in() -> None:
    client = object()

    legacy_gate, legacy_generator, _ = bootstrap._build_decision_components(
        client, separated_decision=False
    )
    gate, generator, verifier = bootstrap._build_decision_components(
        client, separated_decision=True
    )

    assert legacy_gate is None
    assert isinstance(legacy_generator, LLMVerdictGenerator)
    assert isinstance(gate, LLMEvidenceSufficiencyAssessor)
    assert isinstance(generator, LLMConclusiveVerdictGenerator)
    assert isinstance(verifier, GuardedFaithfulnessVerifier)


def test_pipeline_version_is_explicit_and_rejects_unknown_value(monkeypatch) -> None:
    monkeypatch.setenv("PIPELINE_VERSION", "v3")

    assert bootstrap.resolve_pipeline_version(None) == "v3"
    assert bootstrap.resolve_pipeline_version("V1") == "v1"
    with pytest.raises(ValueError, match="PIPELINE_VERSION"):
        bootstrap.resolve_pipeline_version("experimental")


def test_v3_is_default_but_v1_remains_available(monkeypatch) -> None:
    monkeypatch.delenv("PIPELINE_VERSION", raising=False)

    assert bootstrap.resolve_pipeline_version(None) == "v3"
    assert bootstrap.resolve_pipeline_version("v1") == "v1"


def test_configured_builder_dispatches_without_changing_legacy_builder(monkeypatch) -> None:
    legacy = object()
    routed = object()
    monkeypatch.setattr(bootstrap, "build_text_pipeline", lambda **kwargs: legacy)
    monkeypatch.setattr(bootstrap, "build_routed_text_pipeline", lambda **kwargs: routed)

    assert bootstrap.build_configured_text_pipeline(pipeline_version="v1") is legacy
    assert bootstrap.build_configured_text_pipeline(pipeline_version="v3") is routed


def test_routed_builder_freezes_dense_top_fifteen(tmp_path: Path, monkeypatch) -> None:
    corpus_path = tmp_path / "chunks.jsonl"
    write_corpus(corpus_path)
    captured: dict[str, object] = {}
    retriever = object()

    def fake_build_retriever(**kwargs):
        captured.update(kwargs)
        return retriever

    monkeypatch.setattr(bootstrap, "_build_retriever", fake_build_retriever)

    pipeline = bootstrap.build_routed_text_pipeline(corpus_path=corpus_path)

    assert isinstance(pipeline, RoutedFactCheckPipeline)
    assert pipeline.retriever is retriever
    assert captured["top_k"] == 15
    assert captured["retrieval_mode"] == "dense"


def test_v5_is_opt_in_and_dispatched_explicitly(monkeypatch) -> None:
    monkeypatch.delenv("PIPELINE_VERSION", raising=False)
    decomposed = object()
    monkeypatch.setattr(bootstrap, "build_v5_text_pipeline", lambda **kwargs: decomposed)

    assert bootstrap.resolve_pipeline_version(None) == "v3"
    assert bootstrap.build_configured_text_pipeline(pipeline_version="v5") is decomposed


def test_v5_builder_wires_think_only_into_the_judge(monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "_build_retriever", lambda **kwargs: object())

    plain = bootstrap.build_v5_text_pipeline(multi_query=False)
    thinking = bootstrap.build_v5_text_pipeline(think=True)

    assert plain.multi_query is False and thinking.multi_query is True
    assert plain.judge.client.delegate.think is False
    assert thinking.judge.client.delegate.think is True
    assert thinking.extractor.client.delegate.think is False
    assert thinking.judge.max_output_tokens == bootstrap.V5_THINK_OUTPUT_TOKENS
