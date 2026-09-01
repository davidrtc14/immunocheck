from __future__ import annotations

from pathlib import Path

from immunocheck.persistence.database import DatabaseConfigurationError, connect_database
from immunocheck.persistence.migrations import MigrationError, apply_migrations, load_migrations

PROJECT_ROOT = Path(__file__).parents[1]
MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"


def main() -> None:
    try:
        migrations = load_migrations(MIGRATIONS_DIR)
        with connect_database() as connection:
            result = apply_migrations(connection, migrations)
    except (DatabaseConfigurationError, MigrationError, OSError) as exc:
        print(f"FALHA: {exc}")
        raise SystemExit(1) from exc
    print(
        f"Migrations concluídas: {len(result.applied)} aplicada(s), "
        f"{len(result.already_applied)} já existente(s)."
    )


if __name__ == "__main__":
    main()
