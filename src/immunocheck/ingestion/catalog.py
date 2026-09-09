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
    primary_theme: str
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
    "primary_theme",
    "license_status",
    "status",
    "notes",
}

ALLOWED_FORMATS = {"pdf", "html", "xml"}
ALLOWED_STATUSES = {"candidate", "downloaded", "validated", "rejected"}
ALLOWED_PRIMARY_THEMES = {
    "normas_e_calendarios",
    "composicao_e_fabricacao",
    "eficacia_e_imunogenicidade",
    "seguranca_e_farmacovigilancia",
    "contraindicacoes_e_populacoes_especiais",
    "vacinas_especificas",
    "epidemiologia_das_doencas",
    "alegacoes_causais_recorrentes",
    "comunicacao_equidade_e_etica",
}


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
    required_values = (
        "document_id",
        "title",
        "source",
        "document_type",
        "url",
        "format",
        "primary_theme",
    )
    empty = [field for field in required_values if not row[field].strip()]
    if empty:
        raise InvalidCatalogError(f"Campos obrigatórios vazios: {', '.join(empty)}")
    if row["format"] not in ALLOWED_FORMATS:
        raise InvalidCatalogError(f"Formato não aceito no catálogo: {row['format']}")
    if row["status"] not in ALLOWED_STATUSES:
        raise InvalidCatalogError(f"Estado não aceito no catálogo: {row['status']}")
    if row["primary_theme"] not in ALLOWED_PRIMARY_THEMES:
        raise InvalidCatalogError(
            f"Tema primário não aceito no catálogo: {row['primary_theme']}"
        )

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
        primary_theme=row["primary_theme"],
        access_date=row["access_date"],
        license_status=row["license_status"],
        status=row["status"],
        notes=row["notes"],
    )
