from __future__ import annotations

import hashlib
import json
from pathlib import Path

from immunocheck.evaluation.confirmatory import validate_confirmatory_dataset
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_calibration import load_family_ids
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v3/confirmatory/items.jsonl"
CALIBRATION = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
FROZEN_TEST_FAMILIES = ROOT / "evaluation/refinement_v2/FROZEN_TEST_FAMILIES.txt"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v3/confirmatory/manifest.json"
PROTOCOL = ROOT / "evaluation/refinement_v3/confirmatory/PROTOCOL.md"
CANDIDATE_FREEZE = ROOT / "evaluation/refinement_v3/CANDIDATE_FREEZE.md"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "confirmatory_ready_frozen_unexecuted":
        raise RuntimeError("O manifesto não está no estado pré-execução esperado.")
    expected_hashes = {
        DATASET: manifest["dataset_sha256"],
        PROTOCOL: manifest["protocol_sha256"],
        CANDIDATE_FREEZE: manifest["candidate_freeze_sha256"],
    }
    for path, expected in expected_hashes.items():
        if _sha256(path) != expected:
            raise RuntimeError(f"Hash divergente: {path.relative_to(ROOT)}")

    evidence = load_evidence_jsonl(CORPUS)
    valid_chunk_ids = {chunk.chunk_id for chunk in evidence}
    items = load_end_to_end_items(
        DATASET,
        valid_chunk_ids=valid_chunk_ids,
        require_reviewed=False,
    )
    calibration = load_end_to_end_items(CALIBRATION, require_reviewed=True)
    excluded = set(
        load_family_ids(FROZEN_TEST_FAMILIES.read_text("utf-8").splitlines())
    )
    excluded.update(item.claim_family for item in calibration if item.claim_family)
    summary = validate_confirmatory_dataset(items, excluded_families=excluded)
    print(f"Itens: {summary.total}")
    print(f"Famílias inéditas: {summary.families}")
    print(f"Chunks de evidência: {summary.evidence_chunks}")
    print("Classes:", summary.labels)
    print("Temas:", summary.topics)
    print("Estado: gabarito documental congelável; sem revisão externa alegada")
    return 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
