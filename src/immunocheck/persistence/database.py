from __future__ import annotations

import os
from typing import Any


class DatabaseConfigurationError(RuntimeError):
    """Indica configuração ausente ou driver PostgreSQL indisponível."""


def database_url_from_env() -> str:
    value = os.environ.get("DATABASE_URL", "").strip()
    if not value:
        raise DatabaseConfigurationError("Defina DATABASE_URL para acessar o PostgreSQL local.")
    if not value.startswith(("postgresql://", "postgresql+psycopg://")):
        raise DatabaseConfigurationError("DATABASE_URL deve usar o esquema postgresql://.")
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def connect_database(database_url: str | None = None) -> Any:
    try:
        import psycopg
    except ImportError as exc:
        raise DatabaseConfigurationError(
            "Psycopg não está instalado. Reinstale o projeto com suas dependências."
        ) from exc
    return psycopg.connect(database_url or database_url_from_env(), autocommit=True)
