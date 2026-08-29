from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from immunocheck.ingestion.models import DocumentMetadata


class InvalidCatalogError(ValueError):
    """Indica inconsistência estrutural no catálogo do corpus."""


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    metadata: DocumentMetadata
    access_date: str
    license_status: str
    status: str
    notes: str


REQUIRED_COLUMNS = {
    "document_id",
    "title",
    "source",
    "document_type",
    "publication_date",
    "access_date",
    "url",
    "format",
    "license_status",
    "status",
    "notes",
}

ALLOWED_FORMATS = {"pdf", "html"}
ALLOWED_STATUSES = {"candidate", "downloaded", "validated", "rejected"}


def load_catalog(path: Path) -> tuple[CatalogEntry, ...]:
    with path.open(encoding="utf-8", newline="") as catalog_file:
        reader = csv.DictReader(catalog_file)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or ())
        if missing:
            raise InvalidCatalogError(f"Colunas ausentes: {', '.join(sorted(missing))}")
        entries = tuple(_parse_row(row) for row in reader)

    ids = [entry.metadata.document_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise InvalidCatalogError("O catálogo contém document_id duplicado.")
    return entries


def _parse_row(row: dict[str, str]) -> CatalogEntry:
    required_values = ("document_id", "title", "source", "document_type", "url", "format")
    empty = [field for field in required_values if not row[field].strip()]
    if empty:
        raise InvalidCatalogError(f"Campos obrigatórios vazios: {', '.join(empty)}")
    if row["format"] not in ALLOWED_FORMATS:
        raise InvalidCatalogError(f"Formato não aceito no catálogo: {row['format']}")
    if row["status"] not in ALLOWED_STATUSES:
        raise InvalidCatalogError(f"Estado não aceito no catálogo: {row['status']}")

    return CatalogEntry(
        metadata=DocumentMetadata(
            document_id=row["document_id"],
            title=row["title"],
            source=row["source"],
            document_type=row["document_type"],
            publication_date=row["publication_date"] or None,
            url=row["url"],
            format=row["format"],
        ),
        access_date=row["access_date"],
        license_status=row["license_status"],
        status=row["status"],
        notes=row["notes"],
    )
