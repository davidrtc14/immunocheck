from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path

import pytest

from immunocheck.persistence.migrations import (
    Migration,
    MigrationError,
    apply_migrations,
    load_migrations,
)


class Result:
    def __init__(self, rows=()) -> None:
        self.rows = rows

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, applied=()) -> None:
        self.applied = applied
        self.executions: list[tuple[str, object]] = []

    def transaction(self):
        return nullcontext()

    def execute(self, query, params=None, **kwargs):
        self.executions.append((query, params))
        if "SELECT version, checksum" in query:
            return Result(self.applied)
        return Result()


def test_project_migrations_are_contiguous_and_enable_exact_pgvector() -> None:
    root = Path(__file__).parents[1]
    migrations = load_migrations(root / "database" / "migrations")
    sql = migrations[0].sql.lower()
    xml_sql = migrations[1].sql.lower()

    assert [item.version for item in migrations] == ["0001", "0002"]
    assert "create extension if not exists vector" in sql
    assert "vector(1024)" in sql
    assert "to_tsvector('pg_catalog.portuguese'" in sql
    assert "hnsw" not in sql
    assert "ivfflat" not in sql
    assert "telegram" not in sql
    assert "user_message" not in sql
    assert "check (format in ('pdf', 'html', 'xml'))" in xml_sql


def test_migration_runner_is_idempotent_and_detects_drift() -> None:
    migration = Migration("0001", "0001_test.sql", "a" * 64, "SELECT 1;")
    fresh = FakeConnection()

    result = apply_migrations(fresh, (migration,))

    assert result.applied == ("0001",)
    assert result.already_applied == ()
    assert any("SELECT 1" in query for query, _ in fresh.executions)

    existing = FakeConnection(applied=(("0001", "a" * 64),))
    result = apply_migrations(existing, (migration,))
    assert result.already_applied == ("0001",)
    assert not any("SELECT 1" in query for query, _ in existing.executions)

    drifted = FakeConnection(applied=(("0001", "b" * 64),))
    with pytest.raises(MigrationError, match="Checksum divergente"):
        apply_migrations(drifted, (migration,))


def test_migration_loader_rejects_gaps(tmp_path: Path) -> None:
    (tmp_path / "0001_first.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "0003_third.sql").write_text("SELECT 3;", encoding="utf-8")

    with pytest.raises(MigrationError, match="contíguas"):
        load_migrations(tmp_path)
