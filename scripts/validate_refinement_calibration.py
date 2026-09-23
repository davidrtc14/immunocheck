from __future__ import annotations

import argparse
from pathlib import Path

from immunocheck.evaluation.end_to_end import DatasetStatus, load_end_to_end_items
from immunocheck.evaluation.refinement_calibration import (
    load_family_ids,
    validate_refinement_calibration,
)
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "evaluation" / "refinement_v2" / "calibration" / "candidates.jsonl"
DEFAULT_FAMILIES = ROOT / "evaluation" / "refinement_v2" / "FROZEN_TEST_FAMILIES.txt"
CORPUS = ROOT / "corpus" / "processed" / "chunks.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida um estágio da calibração v2.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--frozen-test-families", type=Path, default=DEFAULT_FAMILIES)
    parser.add_argument(
        "--status",
        choices=tuple(status.value for status in DatasetStatus),
        default=DatasetStatus.DRAFT.value,
    )
    args = parser.parse_args()

    evidence = load_evidence_jsonl(CORPUS)
    items = load_end_to_end_items(
        args.dataset,
        valid_chunk_ids={chunk.chunk_id for chunk in evidence},
        require_reviewed=False,
    )
    families = load_family_ids(args.frozen_test_families.read_text(encoding="utf-8").splitlines())
    expected_status = DatasetStatus(args.status)
    summary = validate_refinement_calibration(
        items,
        frozen_test_families=families,
        expected_status=expected_status,
    )

    print(f"Itens: {summary.total}")
    print(f"Famílias inéditas: {summary.families}")
    print(f"Chunks de evidência: {summary.evidence_chunks}")
    print("Classes:", summary.labels)
    print("Temas:", summary.topics)
    if expected_status is DatasetStatus.DRAFT:
        print("Estado: rascunho; revisão humana ainda não incorporada")
    else:
        print("Estado: primeira revisão incorporada; segunda revisão ainda pendente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
