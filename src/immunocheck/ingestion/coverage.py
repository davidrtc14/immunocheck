from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from immunocheck.ingestion.catalog import CatalogEntry


@dataclass(frozen=True, slots=True)
class ThemeCoverage:
    primary_theme: str
    target_min: int
    target_max: int
    cataloged: int
    validated: int
    downloaded: int
    candidate: int
    rejected: int

    @property
    def gap_to_minimum(self) -> int:
        return max(0, self.target_min - self.validated)


def audit_coverage(
    entries: tuple[CatalogEntry, ...], plan_path: Path
) -> tuple[ThemeCoverage, ...]:
    with plan_path.open(encoding="utf-8", newline="") as plan_file:
        plan = tuple(csv.DictReader(plan_file))
    rows = []
    for target in plan:
        theme = target["primary_theme"]
        selected = tuple(entry for entry in entries if entry.primary_theme == theme)
        counts = {
            status: sum(entry.status == status for entry in selected)
            for status in ("validated", "downloaded", "candidate", "rejected")
        }
        rows.append(
            ThemeCoverage(
                primary_theme=theme,
                target_min=int(target["target_min"]),
                target_max=int(target["target_max"]),
                cataloged=len(selected),
                **counts,
            )
        )
    return tuple(rows)


def render_coverage_markdown(rows: tuple[ThemeCoverage, ...]) -> str:
    header = (
        "| Tema primário | Meta | Catalogados | Validados | Baixados | "
        "Candidatos | Rejeitados | Lacuna mínima |\n"
        "|---|---:|---:|---:|---:|---:|---:|---:|"
    )
    body = "\n".join(
        f"| `{row.primary_theme}` | {row.target_min}–{row.target_max} | "
        f"{row.cataloged} | {row.validated} | {row.downloaded} | {row.candidate} | "
        f"{row.rejected} | {row.gap_to_minimum} |"
        for row in rows
    )
    totals = (
        f"\n\nTotais: {sum(row.cataloged for row in rows)} catalogados; "
        f"{sum(row.validated for row in rows)} validados; "
        f"{sum(row.downloaded for row in rows)} baixados não validados; "
        f"lacuna de {sum(row.gap_to_minimum for row in rows)} documentos para o mínimo temático."
    )
    return "# Auditoria de cobertura do corpus\n\n" + header + "\n" + body + totals + "\n"
