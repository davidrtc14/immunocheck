from __future__ import annotations

from contextlib import nullcontext

import pytest

from immunocheck.ingestion.corpus_versioning import CorpusChanges, CorpusSnapshot
from immunocheck.persistence.postgres import (
    BGE_M3_DIMENSION,
    CorpusRepositoryError,
    EmbeddingRecord,
    PostgresCorpusRepository,
)


class Result:
    def __init__(self, *, one=None, rows=()) -> None:
        self.one = one
        self.rows = rows

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.rows


class FakeCursor:
    def __init__(self, batches) -> None:
        self.batches = batches

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def executemany(self, query, rows):
        self.batches.append((query, tuple(rows)))


class FakeConnection:
    def __init__(self) -> None:
        self.existing = None
        self.complete_embeddings = ("BAAI/bge-m3", "revision")
        self.dense_rows = ()
        self.executions: list[tuple[str, object]] = []
        self.batches: list[tuple[str, tuple[object, ...]]] = []

    def transaction(self):
        return nullcontext()

    def cursor(self):
        return FakeCursor(self.batches)

    def execute(self, query, params=None, **_kwargs):
        self.executions.append((query, params))
        if "SELECT chunks_sha256" in query:
            return Result(one=self.existing)
        if "HAVING count(*)" in query:
            return Result(one=self.complete_embeddings)
        if "RETURNING corpus_version" in query:
            return Result(one=(params[0],))
        if "AS similarity" in query:
            return Result(rows=self.dense_rows)
        return Result()


def _snapshot() -> CorpusSnapshot:
    version = "sha256:" + "a" * 64
    document = {
        "document_id": "doc-a",
        "title": "Documento A",
        "source": "Fonte oficial",
        "document_type": "manual",
        "publication_date": "2026-01-01",
        "access_date": "2026-08-31",
        "url": "https://example.gov.br/a.pdf",
        "final_url": "https://example.gov.br/a.pdf",
        "format": "pdf",
        "license_status": "a verificar",
        "content_type": "application/pdf",
        "downloaded_at": "2026-08-31T12:00:00+00:00",
        "content_sha256": "b" * 64,
        "size_bytes": 10,
    }
    chunk = {
        "chunk_id": "doc-a:p1:c1:hash",
        "document_id": "doc-a",
        "text": "Vacinação humana.",
        "chunk_sha256": "c" * 64,
        "page_start": 1,
        "page_end": 1,
        "source": "Fonte oficial",
        "document_title": "Documento A",
        "url": "https://example.gov.br/a.pdf",
        "publication_date": "2026-01-01",
    }
    manifest = {
        "corpus_version": version,
        "schema_version": 1,
        "generated_at": "2026-08-31T12:00:00+00:00",
        "chunks_sha256": "d" * 64,
        "document_count": 1,
        "chunk_count": 1,
        "documents": [document],
    }
    return CorpusSnapshot(
        manifest=manifest,
        chunks=(chunk,),
        report=(),
        changes=CorpusChanges(("doc-a",), (), (), (), ()),
    )


def _unit_vector() -> tuple[float, ...]:
    return (1.0,) + (0.0,) * (BGE_M3_DIMENSION - 1)


def test_import_snapshot_is_transactional_and_idempotent() -> None:
    connection = FakeConnection()
    repository = PostgresCorpusRepository(connection)

    result = repository.import_snapshot(_snapshot(), activate=True)

    assert result.inserted is True
    assert result.activated is True
    assert len(connection.batches) == 2
    assert len(connection.batches[0][1]) == 1
    assert len(connection.batches[1][1]) == 1
    assert any("SET state = 'ACTIVE'" in query for query, _ in connection.executions)

    connection.existing = ("d" * 64, 1, 1, _snapshot().manifest)
    connection.batches.clear()
    result = repository.import_snapshot(_snapshot())
    assert result.inserted is False
    assert connection.batches == []


def test_existing_version_with_different_metadata_is_rejected() -> None:
    connection = FakeConnection()
    connection.existing = ("0" * 64, 1, 1, _snapshot().manifest)

    with pytest.raises(CorpusRepositoryError, match="incompatíveis"):
        PostgresCorpusRepository(connection).import_snapshot(_snapshot())


def test_activation_requires_complete_embeddings() -> None:
    connection = FakeConnection()
    connection.complete_embeddings = None

    with pytest.raises(CorpusRepositoryError, match="conjunto completo"):
        PostgresCorpusRepository(connection).import_snapshot(_snapshot(), activate=True)


def test_embedding_batch_validates_dimension_normalization_and_duplicates() -> None:
    repository = PostgresCorpusRepository(FakeConnection())
    kwargs = {
        "corpus_version": "sha256:" + "a" * 64,
        "model_name": "BAAI/bge-m3",
        "model_revision": "revision",
    }

    with pytest.raises(CorpusRepositoryError, match="1024"):
        repository.upsert_embeddings(**kwargs, embeddings=(EmbeddingRecord("chunk", (1.0,)),))
    with pytest.raises(CorpusRepositoryError, match="normalizado"):
        repository.upsert_embeddings(
            **kwargs,
            embeddings=(EmbeddingRecord("chunk", (1.0,) * BGE_M3_DIMENSION),),
        )
    with pytest.raises(CorpusRepositoryError, match="duplicado"):
        repository.upsert_embeddings(
            **kwargs,
            embeddings=(
                EmbeddingRecord("chunk", _unit_vector()),
                EmbeddingRecord("chunk", _unit_vector()),
            ),
        )


def test_embedding_upsert_and_exact_dense_result() -> None:
    connection = FakeConnection()
    repository = PostgresCorpusRepository(connection)
    count = repository.upsert_embeddings(
        corpus_version="sha256:" + "a" * 64,
        model_name="BAAI/bge-m3",
        model_revision="revision",
        embeddings=(EmbeddingRecord("chunk", _unit_vector()),),
    )
    assert count == 1
    assert "::vector" in connection.batches[0][0]

    connection.dense_rows = (
        (
            "chunk",
            "Vacinação humana.",
            "Fonte",
            "Documento",
            "https://example.gov.br",
            "2026-01-01",
            1,
            0.75,
        ),
    )
    result = repository.search_active_dense(
        _unit_vector(),
        model_name="BAAI/bge-m3",
        model_revision="revision",
        top_k=1,
    )
    assert result[0].chunk_id == "chunk"
    assert result[0].retrieval_score == 0.75
    query = connection.executions[-1][0]
    assert "<=>" in query
    assert "v.state = 'ACTIVE'" in query
