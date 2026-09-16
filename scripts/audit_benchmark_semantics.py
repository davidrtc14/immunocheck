"""Ranqueia similaridade entre splits; não classifica nem modifica o benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items
from immunocheck.evaluation.semantic_audit import rank_cross_split_semantic_pairs
from immunocheck.retrieval.dense import (
    BGE_M3_MODEL,
    BGE_M3_REVISION,
    SentenceTransformerEmbedder,
)

ROOT = Path(__file__).parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Triagem local de possíveis paráfrases entre desenvolvimento e teste."
    )
    parser.add_argument("--dataset", type=Path, default=ROOT / "evaluation/end_to_end/items.jsonl")
    parser.add_argument("--development-to-test", required=True)
    parser.add_argument("--test-to-development", required=True)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    items = load_end_to_end_items(args.dataset, require_reviewed=True)
    adjusted = tuple(
        replace(item, split=DatasetSplit.TEST)
        if item.claim_family == args.development_to_test
        else replace(item, split=DatasetSplit.DEVELOPMENT)
        if item.claim_family == args.test_to_development
        else item
        for item in items
    )
    if sum(item.claim_family == args.development_to_test for item in items) == 0:
        parser.error("Família development-to-test ausente.")
    if sum(item.claim_family == args.test_to_development for item in items) == 0:
        parser.error("Família test-to-development ausente.")
    embedder = SentenceTransformerEmbedder(
        cache_folder=ROOT / "models", local_files_only=True, batch_size=8
    )
    vectors = embedder.encode(tuple(item.claim for item in adjusted))
    pairs = rank_cross_split_semantic_pairs(adjusted, vectors, limit=args.limit)
    family_pair_maxima: dict[tuple[str, str], float] = {}
    for pair in pairs:
        key = (pair.development_family, pair.test_family)
        family_pair_maxima[key] = max(
            pair.cosine_similarity,
            family_pair_maxima.get(key, float("-inf")),
        )
    identity = hashlib.sha256(
        "".join(
            f"{item.item_id}\t{item.split.value}\t{item.claim_family}\t{item.claim}\n"
            for item in adjusted
        ).encode("utf-8")
    ).hexdigest()
    print(
        json.dumps(
            {
                "purpose": "human_review_candidates_not_automatic_leakage_decisions",
                "dataset_identity_sha256": identity,
                "model": BGE_M3_MODEL,
                "model_revision": BGE_M3_REVISION,
                "normalized_cosine": True,
                "development_to_test": args.development_to_test,
                "test_to_development": args.test_to_development,
                "pair_count_reviewed_by_ranking": len(pairs),
                "top_ranked_family_pairs": [
                    {
                        "development_family": development_family,
                        "test_family": test_family,
                        "maximum_cosine_similarity_in_ranked_pairs": similarity,
                    }
                    for (development_family, test_family), similarity in sorted(
                        family_pair_maxima.items(), key=lambda entry: (-entry[1], entry[0])
                    )
                ],
                "pairs": [asdict(pair) for pair in pairs],
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
