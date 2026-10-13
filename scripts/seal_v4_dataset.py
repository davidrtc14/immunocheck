"""Gera o manifesto de lacre do conjunto v4 (hashes de itens e protocolo, sem executar nada)."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from immunocheck.evaluation.end_to_end import load_end_to_end_items

REPOSITORY = Path(__file__).resolve().parents[1]
ROOT = REPOSITORY / "evaluation/refinement_v4"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manifesto de lacre do v4.")
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    target = ROOT / "manifest.json"
    if target.exists() and not args.overwrite:
        parser.error("Manifesto já existe; alterá-lo invalida o lacre.")

    items = load_end_to_end_items(ROOT / "items.jsonl", require_reviewed=True)
    holdout = sorted(item.item_id for item in items if item.split.value == "test")
    manifest = {
        "schema_version": 1,
        "status": "sealed_unexecuted",
        "created_at": args.created_at,
        "dataset": "evaluation/refinement_v4/items.jsonl",
        "dataset_sha256": sha256(ROOT / "items.jsonl"),
        "protocol": "evaluation/refinement_v4/PROTOCOL.md",
        "protocol_sha256": sha256(ROOT / "PROTOCOL.md"),
        "item_count": len(items),
        "family_count": len({item.claim_family for item in items}),
        "labels": dict(sorted(Counter(item.label.value for item in items).items())),
        "splits": dict(sorted(Counter(item.split.value for item in items).items())),
        "holdout_item_ids_sha256": hashlib.sha256("\n".join(holdout).encode()).hexdigest(),
        "curation": "project_researcher_ai_assisted",
        "external_human_review_claimed": False,
        "second_annotation_completed": False,
        "holdout_inference_executed": False,
        "retrieval_ablation_executed_on_calibration": True,
        "end_to_end_inference_executed": False,
    }
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
