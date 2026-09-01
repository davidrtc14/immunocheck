from __future__ import annotations

import argparse
from pathlib import Path

from immunocheck.ingestion.catalog import load_catalog
from immunocheck.ingestion.coverage import audit_coverage, render_coverage_markdown

PROJECT_ROOT = Path(__file__).parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita cobertura temática do catálogo.")
    parser.add_argument("--output", type=Path, help="Arquivo Markdown opcional.")
    args = parser.parse_args()
    report = render_coverage_markdown(
        audit_coverage(
            load_catalog(PROJECT_ROOT / "corpus" / "catalog.csv"),
            PROJECT_ROOT / "corpus" / "coverage_plan.csv",
        )
    )
    if args.output:
        output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
