from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{4})_[a-z0-9_]+\.sql$")


class MigrationError(RuntimeError):
    """Indica falha, lacuna ou divergência no histórico de migrations."""


class DatabaseConnection(Protocol):
    def execute(
        self,
        query: str,
        params: Sequence[object] | None = None,
        **kwargs: object,
    ) -> Any: ...

    def transaction(self) -> Any: ...


@dataclass(frozen=True, slots=True)
class Migration:
    version: str
    name: str
    checksum: str
    sql: str


@dataclass(frozen=True, slots=True)
class MigrationResult:
    applied: tuple[str, ...]
    already_applied: tuple[str, ...]


def load_migrations(directory: Path) -> tuple[Migration, ...]:
    if not directory.is_dir():
        raise MigrationError(f"Diretório de migrations ausente: {directory}")
    migrations: list[Migration] = []
    for path in sorted(directory.glob("*.sql")):
        match = MIGRATION_NAME.fullmatch(path.name)
        if match is None:
            raise MigrationError(f"Nome de migration inválido: {path.name}")
        try:
            sql = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise MigrationError(f"Não foi possível ler {path.name}.") from exc
        if not sql.strip():
            raise MigrationError(f"Migration vazia: {path.name}")
        migrations.append(
            Migration(
                version=match.group("version"),
                name=path.name,
                checksum=hashlib.sha256(sql.encode("utf-8")).hexdigest(),
                sql=sql,
            )
        )

    if not migrations:
        raise MigrationError("Nenhuma migration foi encontrada.")
    versions = [migration.version for migration in migrations]
    if len(versions) != len(set(versions)):
        raise MigrationError("Há versões de migration duplicadas.")
    expected = [f"{number:04d}" for number in range(1, len(migrations) + 1)]
    if versions != expected:
        raise MigrationError("As migrations devem começar em 0001 e ser contíguas.")
    return tuple(migrations)


def apply_migrations(
    connection: DatabaseConnection,
    migrations: Sequence[Migration],
) -> MigrationResult:
    with connection.transaction():
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS immunocheck_schema_migrations (
                version text PRIMARY KEY,
                name text NOT NULL,
                checksum char(64) NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    rows = connection.execute(
        "SELECT version, checksum FROM immunocheck_schema_migrations ORDER BY version"
    ).fetchall()
    applied_checksums = {str(version): str(checksum) for version, checksum in rows}

    applied: list[str] = []
    already_applied: list[str] = []
    for migration in migrations:
        existing = applied_checksums.get(migration.version)
        if existing is not None:
            if existing != migration.checksum:
                raise MigrationError(
                    f"Checksum divergente para a migration {migration.version}; "
                    "não altere migrations já aplicadas."
                )
            already_applied.append(migration.version)
            continue
        with connection.transaction():
            connection.execute(migration.sql, prepare=False)
            connection.execute(
                """
                INSERT INTO immunocheck_schema_migrations (version, name, checksum)
                VALUES (%s, %s, %s)
                """,
                (migration.version, migration.name, migration.checksum),
            )
        applied.append(migration.version)
    return MigrationResult(tuple(applied), tuple(already_applied))
