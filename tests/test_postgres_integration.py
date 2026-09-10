from __future__ import annotations

import os
from pathlib import Path

import pytest

from immunocheck.persistence.database import connect_database
from immunocheck.persistence.migrations import apply_migrations, load_migrations


def test_migrations_apply_to_real_pgvector_database() -> None:
    database_url = os.environ.get("IMMUNOCHECK_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("IMMUNOCHECK_TEST_DATABASE_URL não configurada")
    migrations = load_migrations(Path(__file__).parents[1] / "database" / "migrations")
    with connect_database(database_url) as connection:
        apply_migrations(connection, migrations)
        extension = connection.execute(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
        ).fetchone()
        dimension = connection.execute(
            """
            SELECT atttypmod
            FROM pg_attribute
            WHERE attrelid = 'chunk_embeddings'::regclass AND attname = 'embedding'
            """
        ).fetchone()
        format_constraint = connection.execute(
            """
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'corpus_documents'::regclass
              AND conname = 'corpus_documents_format_check'
            """
        ).fetchone()
    assert extension is not None
    assert dimension == (1024,)
    assert format_constraint is not None
    assert "'xml'::text" in format_constraint[0]
