"""Baseline lexical (A4) sobre a calibração v4: mede atalhos de redação, não valida o sistema."""

from __future__ import annotations

import argparse
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import sklearn

from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items
from immunocheck.evaluation.lexical_baseline import (
    LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES,
    LEXICAL_BASELINE_FOLDS,
    LEXICAL_BASELINE_SEED,
    evaluate_lexical_baseline,
)

REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/refinement_v4/results/lexical_baseline_calibration.json"
# Gate pré-registrado em PROTOCOL.md: abaixo disso o conjunto não revela atalho lexical forte.
MAXIMUM_BASELINE_MACRO_F1 = 0.45


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline lexical na calibração v4.")
    parser.add_argument("--items", type=Path, default=DEFAULT_ITEMS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Resultado já existe; use --overwrite somente para reprodução declarada.")

    items = load_end_to_end_items(args.items, require_reviewed=True)
    calibration = tuple(item for item in items if item.split is DatasetSplit.DEVELOPMENT)
    report = evaluate_lexical_baseline(
        calibration,
        folds=LEXICAL_BASELINE_FOLDS,
        seed=LEXICAL_BASELINE_SEED,
        bootstrap_resamples=LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES,
    )
    macro_f1 = float(report["metrics"]["macro_f1"])  # type: ignore[index]
    report.update(
        {
            "partition": "calibration_v4",
            "holdout_items_loaded_into_model": False,
            "executed_at": datetime.now(UTC).isoformat(),
            "gate": {
                "maximum_macro_f1": MAXIMUM_BASELINE_MACRO_F1,
                "observed_macro_f1": macro_f1,
                "passed": macro_f1 <= MAXIMUM_BASELINE_MACRO_F1,
            },
            "environment": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scikit_learn": sklearn.__version__,
            },
        }
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(json.dumps(report["gate"], indent=2))


if __name__ == "__main__":
    main()
