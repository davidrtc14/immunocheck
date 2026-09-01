from __future__ import annotations

import argparse
from pathlib import Path

from immunocheck.ingestion.corpus_versioning import (
    CorpusVersioningError,
    load_published_corpus,
)
from immunocheck.persistence.database import DatabaseConfigurationError, connect_database
from immunocheck.persistence.postgres import CorpusRepositoryError, PostgresCorpusRepository

PROJECT_ROOT = Path(__file__).parents[1]
PROCESSED_DIR = PROJECT_ROOT / "corpus" / "processed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa uma versão validada do corpus.")
    parser.add_argument(
        "--activate",
        action="store_true",
        help="ativa a versão importada e arquiva a versão anteriormente ativa",
    )
    args = parser.parse_args()
    try:
        snapshot = load_published_corpus(
            manifest_path=PROCESSED_DIR / "manifest.json",
            chunks_path=PROCESSED_DIR / "chunks.jsonl",
            report_path=PROCESSED_DIR / "validation_report.json",
        )
        with connect_database() as connection:
            result = PostgresCorpusRepository(connection).import_snapshot(
                snapshot, activate=args.activate
            )
    except (CorpusVersioningError, CorpusRepositoryError, DatabaseConfigurationError) as exc:
        print(f"FALHA: {exc}")
        raise SystemExit(1) from exc
    action = "importada" if result.inserted else "já existente"
    activation = " e ativada" if result.activated else ""
    print(
        f"Versão {result.corpus_version} {action}{activation}: "
        f"{result.document_count} documento(s), {result.chunk_count} chunk(s)."
    )


if __name__ == "__main__":
    main()
