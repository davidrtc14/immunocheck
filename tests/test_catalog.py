from pathlib import Path

import pytest

from immunocheck.ingestion.catalog import InvalidCatalogError, load_catalog


def test_project_catalog_is_valid_and_has_unique_ids() -> None:
    catalog_path = Path(__file__).parents[1] / "corpus" / "catalog.csv"

    entries = load_catalog(catalog_path)

    assert len(entries) >= 8
    assert len({entry.metadata.document_id for entry in entries}) == len(entries)
    assert {entry.metadata.format for entry in entries} == {"pdf", "html", "xml"}
    assert all(entry.primary_theme for entry in entries)


def test_catalog_rejects_duplicated_ids(tmp_path: Path) -> None:
    catalog = tmp_path / "catalog.csv"
    catalog.write_text(
        "document_id,title,source,document_type,publication_date,access_date,url,format,"
        "primary_theme,license_status,status,notes\n"
        "same,A,S,manual,2024-01-01,2026-01-01,https://a.example/a.pdf,pdf,"
        "normas_e_calendarios,ok,candidate,n\n"
        "same,B,S,manual,2024-01-01,2026-01-01,https://a.example/b.pdf,pdf,"
        "normas_e_calendarios,ok,candidate,n\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidCatalogError, match="duplicado"):
        load_catalog(catalog)
