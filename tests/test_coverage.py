from pathlib import Path

from immunocheck.ingestion.catalog import load_catalog
from immunocheck.ingestion.coverage import audit_coverage, render_coverage_markdown


def test_project_coverage_audit_accounts_for_every_catalog_entry() -> None:
    root = Path(__file__).parents[1]
    entries = load_catalog(root / "corpus" / "catalog.csv")
    rows = audit_coverage(entries, root / "corpus" / "coverage_plan.csv")

    assert len(rows) == 9
    assert sum(row.cataloged for row in rows) == len(entries)
    assert sum(row.validated for row in rows) == sum(
        entry.status == "validated" for entry in entries
    )
    assert all(row.gap_to_minimum >= 0 for row in rows)
    assert "Lacuna mínima" in render_coverage_markdown(rows)
