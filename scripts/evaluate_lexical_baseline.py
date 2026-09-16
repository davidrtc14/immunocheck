"""Executa o baseline pré-registrado somente no split de desenvolvimento."""

from __future__ import annotations

import argparse
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import sklearn

from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.lexical_baseline import (
    LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES,
    LEXICAL_BASELINE_FOLDS,
    LEXICAL_BASELINE_SEED,
    evaluate_lexical_baseline,
    load_frozen_development_items,
)

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/development/lexical_baseline.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline lexical no desenvolvimento congelado.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Resultado já existe; não sobrescrever a primeira execução sem --overwrite.")

    manifest = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    report = evaluate_lexical_baseline(
        items,
        folds=LEXICAL_BASELINE_FOLDS,
        seed=LEXICAL_BASELINE_SEED,
        bootstrap_resamples=LEXICAL_BASELINE_BOOTSTRAP_RESAMPLES,
    )
    report.update(
        {
            "executed_at": datetime.now(UTC).isoformat(),
            "protocol": "evaluation/EXPERIMENT_PROTOCOL.md",
            "freeze_id": manifest["freeze_id"],
            "frozen_dataset_sha256": manifest["frozen_dataset_sha256"],
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
    metrics = report["metrics"]
    intervals = report["bootstrap_95_percentile_interval"]
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}")
    print(
        f"Macro-F1={metrics['macro_f1']:.3f} "
        f"(IC95% {intervals['macro_f1']['lower']:.3f}–"
        f"{intervals['macro_f1']['upper']:.3f})"
    )
    print(f"Balanced accuracy={metrics['balanced_accuracy']:.3f}")
    print(f"Acurácia={metrics['accuracy']:.3f}")


if __name__ == "__main__":
    main()
