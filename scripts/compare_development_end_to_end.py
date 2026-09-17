"""Compara de forma pareada as iterações fim a fim v1 e v2."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.evaluation.development_end_to_end import (
    END_TO_END_BOOTSTRAP_RESAMPLES,
    END_TO_END_BOOTSTRAP_SEED,
    compare_end_to_end_iterations,
    load_checkpoint,
    sha256_file,
)
from immunocheck.evaluation.lexical_baseline import load_frozen_development_items

REPOSITORY = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"
BASELINE = REPOSITORY / "evaluation/results/development/end_to_end_records.jsonl"
CANDIDATE = REPOSITORY / "evaluation/results/development/end_to_end_v2_records.jsonl"
OUTPUT = REPOSITORY / "evaluation/results/development/end_to_end_v1_v2_comparison.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara as iterações fim a fim v1 e v2.")
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Comparação já existe; não sobrescrever o artefato publicado.")

    freeze = validate_freeze_manifest(root=BENCHMARK_ROOT)
    items = load_frozen_development_items(BENCHMARK_ROOT)
    baseline = load_checkpoint(args.baseline)
    candidate = load_checkpoint(args.candidate)
    comparison = compare_end_to_end_iterations(
        baseline,
        candidate,
        items,
        bootstrap_resamples=END_TO_END_BOOTSTRAP_RESAMPLES,
        seed=END_TO_END_BOOTSTRAP_SEED,
    )
    report = {
        "schema_version": 1,
        "executed_at": datetime.now(UTC).isoformat(),
        "partition": "development",
        "test_items_loaded": 0,
        "freeze_id": freeze["freeze_id"],
        "frozen_dataset_sha256": freeze["frozen_dataset_sha256"],
        "baseline_path": str(args.baseline.relative_to(REPOSITORY)).replace("\\", "/"),
        "baseline_sha256": sha256_file(args.baseline),
        "candidate_path": str(args.candidate.relative_to(REPOSITORY)).replace("\\", "/"),
        "candidate_sha256": sha256_file(args.candidate),
        "comparison": comparison,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Comparação salva em {args.output.relative_to(REPOSITORY)}")


if __name__ == "__main__":
    main()
