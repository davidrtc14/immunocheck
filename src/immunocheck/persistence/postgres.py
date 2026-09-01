from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from immunocheck.domain.models import Evidence
from immunocheck.ingestion.corpus_versioning import CorpusSnapshot

BGE_M3_DIMENSION = 1_024


class CorpusRepositoryError(RuntimeError):
    """Indica violação de integridade ou falha de uso do repositório de corpus."""


class DatabaseConnection(Protocol):
    def execute(
        self,
        query: str,
        params: Sequence[object] | None = None,
        **kwargs: object,
    ) -> Any: ...

    def cursor(self) -> Any: ...

    def transaction(self) -> Any: ...


@dataclass(frozen=True, slots=True)
class CorpusImportResult:
    corpus_version: str
    inserted: bool
    activated: bool
    document_count: int
    chunk_count: int


@dataclass(frozen=True, slots=True)
class EmbeddingRecord:
    chunk_id: str
    values: Sequence[float]


class PostgresCorpusRepository:
    def __init__(self, connection: DatabaseConnection) -> None:
        self._connection = connection

    def import_snapshot(
        self,
        snapshot: CorpusSnapshot,
        *,
        activate: bool = False,
    ) -> CorpusImportResult:
        manifest = snapshot.manifest
        documents = _documents(manifest)
        _validate_snapshot(snapshot, documents)
        corpus_version = str(manifest["corpus_version"])

        with self._connection.transaction():
            existing = self._connection.execute(
                """
                SELECT chunks_sha256, document_count, chunk_count, manifest
                FROM corpus_versions
                WHERE corpus_version = %s
                """,
                (corpus_version,),
            ).fetchone()
            inserted = existing is None
            if existing is not None:
                expected = (
                    str(manifest["chunks_sha256"]),
                    int(manifest["document_count"]),
                    int(manifest["chunk_count"]),
                )
                actual = (str(existing[0]), int(existing[1]), int(existing[2]))
                existing_manifest = existing[3]
                if isinstance(existing_manifest, str):
                    try:
                        existing_manifest = json.loads(existing_manifest)
                    except json.JSONDecodeError as exc:
                        raise CorpusRepositoryError(
                            "O manifesto existente no banco está inválido."
                        ) from exc
                if actual != expected or _json(existing_manifest) != _json(manifest):
                    raise CorpusRepositoryError("A versão já existe com metadados incompatíveis.")
            else:
                self._insert_version(manifest)
                self._insert_documents(corpus_version, documents)
                self._insert_chunks(corpus_version, snapshot.chunks)
            if activate:
                self._activate(corpus_version)

        return CorpusImportResult(
            corpus_version=corpus_version,
            inserted=inserted,
            activated=activate,
            document_count=len(documents),
            chunk_count=len(snapshot.chunks),
        )

    def upsert_embeddings(
        self,
        *,
        corpus_version: str,
        model_name: str,
        model_revision: str,
        embeddings: Sequence[EmbeddingRecord],
        normalized: bool = True,
    ) -> int:
        if not embeddings:
            raise CorpusRepositoryError("Nenhum embedding foi informado.")
        if not model_name.strip() or not model_revision.strip():
            raise CorpusRepositoryError("Modelo e revisão do embedding são obrigatórios.")
        ids = [item.chunk_id for item in embeddings]
        if len(ids) != len(set(ids)):
            raise CorpusRepositoryError("Há chunk_id duplicado no lote de embeddings.")
        rows = [
            (
                corpus_version,
                item.chunk_id,
                model_name,
                model_revision,
                _vector_literal(item.values, require_normalized=normalized),
                normalized,
            )
            for item in embeddings
        ]
        with self._connection.transaction(), self._connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO chunk_embeddings (
                    corpus_version, chunk_id, model_name, model_revision,
                    embedding, normalized
                )
                VALUES (%s, %s, %s, %s, %s::vector, %s)
                ON CONFLICT (corpus_version, chunk_id, model_name, model_revision)
                DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    normalized = EXCLUDED.normalized,
                    generated_at = CURRENT_TIMESTAMP
                """,
                rows,
            )
        return len(rows)

    def search_active_dense(
        self,
        query_vector: Sequence[float],
        *,
        model_name: str,
        model_revision: str,
        top_k: int = 10,
    ) -> tuple[Evidence, ...]:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        vector = _vector_literal(query_vector, require_normalized=True)
        rows = self._connection.execute(
            """
            SELECT
                c.chunk_id,
                c.text_content,
                c.source_name,
                c.document_title,
                c.source_url,
                c.publication_date::text,
                c.page_start,
                1 - (e.embedding <=> %s::vector) AS similarity
            FROM corpus_versions AS v
            JOIN corpus_chunks AS c USING (corpus_version)
            JOIN chunk_embeddings AS e
              ON e.corpus_version = c.corpus_version AND e.chunk_id = c.chunk_id
            WHERE v.state = 'ACTIVE'
              AND e.model_name = %s
              AND e.model_revision = %s
            ORDER BY e.embedding <=> %s::vector, c.chunk_id
            LIMIT %s
            """,
            (vector, model_name, model_revision, vector, top_k),
        ).fetchall()
        return tuple(
            Evidence(
                chunk_id=str(row[0]),
                text=str(row[1]),
                source_name=str(row[2]),
                document_title=str(row[3]),
                url=str(row[4]),
                publication_date=str(row[5]) if row[5] is not None else None,
                page=int(row[6]),
                retrieval_score=float(row[7]),
            )
            for row in rows
        )

    def _insert_version(self, manifest: Mapping[str, object]) -> None:
        self._connection.execute(
            """
            INSERT INTO corpus_versions (
                corpus_version, schema_version, generated_at, chunks_sha256,
                document_count, chunk_count, manifest
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                manifest["corpus_version"],
                manifest["schema_version"],
                manifest["generated_at"],
                manifest["chunks_sha256"],
                manifest["document_count"],
                manifest["chunk_count"],
                _json(manifest),
            ),
        )

    def _insert_documents(
        self,
        corpus_version: str,
        documents: Sequence[Mapping[str, object]],
    ) -> None:
        rows = [
            (
                corpus_version,
                item["document_id"],
                item["title"],
                item["source"],
                item["document_type"],
                item["publication_date"],
                item["access_date"],
                item["url"],
                item["final_url"],
                item["format"],
                item["license_status"],
                item["content_type"],
                item["downloaded_at"],
                item["content_sha256"],
                item["size_bytes"],
                _json(item),
            )
            for item in documents
        ]
        with self._connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO corpus_documents (
                    corpus_version, document_id, title, source_name, document_type,
                    publication_date, access_date, source_url, final_url, format,
                    license_status, content_type, downloaded_at, content_sha256,
                    size_bytes, metadata
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s::jsonb
                )
                """,
                rows,
            )

    def _insert_chunks(
        self,
        corpus_version: str,
        chunks: Sequence[Mapping[str, object]],
    ) -> None:
        rows = [
            (
                corpus_version,
                item["chunk_id"],
                item["document_id"],
                item["text"],
                item["chunk_sha256"],
                item["page_start"],
                item["page_end"],
                item["source"],
                item["document_title"],
                item["url"],
                item["publication_date"],
                _json(item),
            )
            for item in chunks
        ]
        with self._connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO corpus_chunks (
                    corpus_version, chunk_id, document_id, text_content,
                    chunk_sha256, page_start, page_end, source_name, document_title,
                    source_url, publication_date, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                rows,
            )

    def _activate(self, corpus_version: str) -> None:
        complete_embeddings = self._connection.execute(
            """
            SELECT e.model_name, e.model_revision
            FROM corpus_versions AS v
            JOIN chunk_embeddings AS e USING (corpus_version)
            WHERE v.corpus_version = %s
            GROUP BY v.chunk_count, e.model_name, e.model_revision
            HAVING count(*) = v.chunk_count
            LIMIT 1
            """,
            (corpus_version,),
        ).fetchone()
        if complete_embeddings is None:
            raise CorpusRepositoryError(
                "A versão só pode ser ativada após importar um conjunto completo de embeddings."
            )
        self._connection.execute(
            """
            UPDATE corpus_versions
            SET state = 'ARCHIVED'
            WHERE state = 'ACTIVE' AND corpus_version <> %s
            """,
            (corpus_version,),
        )
        updated = self._connection.execute(
            """
            UPDATE corpus_versions
            SET state = 'ACTIVE', activated_at = CURRENT_TIMESTAMP
            WHERE corpus_version = %s
            RETURNING corpus_version
            """,
            (corpus_version,),
        ).fetchone()
        if updated is None:
            raise CorpusRepositoryError("A versão solicitada para ativação não existe.")


def _documents(manifest: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    value = manifest.get("documents")
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise CorpusRepositoryError("O manifesto não possui documentos válidos.")
    return tuple(value)


def _validate_snapshot(
    snapshot: CorpusSnapshot,
    documents: Sequence[Mapping[str, object]],
) -> None:
    manifest = snapshot.manifest
    if manifest.get("document_count") != len(documents):
        raise CorpusRepositoryError("A contagem de documentos diverge do manifesto.")
    if manifest.get("chunk_count") != len(snapshot.chunks):
        raise CorpusRepositoryError("A contagem de chunks diverge do manifesto.")
    document_ids = {item.get("document_id") for item in documents}
    chunk_ids = [item.get("chunk_id") for item in snapshot.chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise CorpusRepositoryError("Há chunk_id duplicado no snapshot.")
    if any(item.get("document_id") not in document_ids for item in snapshot.chunks):
        raise CorpusRepositoryError("Há chunk sem documento correspondente no snapshot.")


def _vector_literal(values: Sequence[float], *, require_normalized: bool) -> str:
    if len(values) != BGE_M3_DIMENSION:
        raise CorpusRepositoryError(f"O embedding deve possuir {BGE_M3_DIMENSION} dimensões.")
    numbers = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in numbers):
        raise CorpusRepositoryError("O embedding contém valor não finito.")
    norm = math.sqrt(sum(value * value for value in numbers))
    if norm == 0:
        raise CorpusRepositoryError("O embedding não pode ser nulo.")
    if require_normalized and not math.isclose(norm, 1.0, rel_tol=1e-3, abs_tol=1e-3):
        raise CorpusRepositoryError("O embedding deve estar normalizado.")
    return "[" + ",".join(format(value, ".9g") for value in numbers) + "]"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
