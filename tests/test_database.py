from __future__ import annotations

import psycopg
import pytest

from immunocheck.persistence.database import DatabaseConfigurationError, connect_database


def test_connect_database_translates_driver_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_connect(*_args, **_kwargs):
        raise psycopg.OperationalError("offline")

    monkeypatch.setattr(psycopg, "connect", fail_connect)

    with pytest.raises(DatabaseConfigurationError, match="PostgreSQL local"):
        connect_database("postgresql://localhost/immunocheck")
