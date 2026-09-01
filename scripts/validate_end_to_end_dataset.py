from __future__ import annotations

import argparse
from pathlib import Path

from immunocheck.evaluation.end_to_end import (
    load_end_to_end_items,
    summarize_end_to_end_items,
    validate_dataset_ready,
)
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

PROJECT_ROOT = Path(__file__).parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "evaluation" / "end_to_end" / "items.jsonl"
CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida o dataset fim a fim do ImmunoCheck.")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument(
        "--ready",
        action="store_true",
        help="Exige todos os critérios mínimos da Fase 5.",
    )
    args = parser.parse_args()

    evidence = load_evidence_jsonl(CORPUS_PATH)
    items = load_end_to_end_items(
        args.path,
        valid_chunk_ids={item.chunk_id for item in evidence},
        require_reviewed=args.ready,
    )
    summary = validate_dataset_ready(items) if args.ready else summarize_end_to_end_items(items)
    print(f"Itens: {summary.total}; revisados: {summary.reviewed}")
    print(
        f"Segunda revisão: {summary.second_reviewed} "
        f"({summary.second_review_fraction:.1%} dos revisados)"
    )
    print("Classes:", summary.labels)
    print("Splits:", summary.splits)
    print("Temas:", summary.topics)


if __name__ == "__main__":
    main()
