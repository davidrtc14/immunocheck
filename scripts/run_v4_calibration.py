"""Executa as condições D1/D2 na calibração v4 (checkpoint retomável; sem holdout)."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from immunocheck.bootstrap import build_v4_text_pipeline
from immunocheck.application.abstention import AbstentionThresholds
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
OUTPUT_DIR = REPOSITORY / "evaluation/refinement_v4/results"
CONDITIONS = {
    "v3_plain": {"grounded": False, "d4": False},
    "v4_grounded": {"grounded": True, "d4": False},
    "v4_d4": {"grounded": True, "d4": True},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibração D1/D2 na partição development.")
    parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    items = [
        item
        for item in load_end_to_end_items(ITEMS, require_reviewed=True)
        if item.split is DatasetSplit.DEVELOPMENT
    ]
    items.sort(key=lambda item: item.item_id)
    if args.limit:
        items = items[: args.limit]

    checkpoint = OUTPUT_DIR / f"calibration_{args.condition}.jsonl"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if checkpoint.exists():
        done = {json.loads(line)["item_id"] for line in checkpoint.read_text("utf-8").splitlines() if line}

    pipeline = build_v4_text_pipeline(
        **CONDITIONS[args.condition], thresholds=AbstentionThresholds()
    )
    with checkpoint.open("a", encoding="utf-8", newline="\n") as handle:
        for item in items:
            if item.item_id in done:
                continue
            pipeline.last_signals = None
            started = time.perf_counter()
            failure = None
            try:
                result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=item.claim))
                verdict = result.verdict.value
                source_ids = [source.chunk_id for source in result.sources]
            except Exception as exc:  # noqa: BLE001 - falha técnica é dado do experimento
                verdict, source_ids, failure = Verdict.INSUFFICIENT_EVIDENCE.value, [], type(exc).__name__
            latency_ms = (time.perf_counter() - started) * 1000
            signals = pipeline.last_signals
            record = {
                "item_id": item.item_id,
                "claim_family": item.claim_family,
                "expected_label": item.label.value,
                "verdict": verdict,
                "source_ids": source_ids,
                "latency_ms": round(latency_ms, 1),
                "failure": failure,
                "signals": asdict(signals) if signals else None,
                "route": pipeline.last_route,
                "technical_abstention": pipeline.last_technical_abstention,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(item.item_id, item.label.value, "->", verdict, f"{latency_ms / 1000:.1f}s", failure or "")


if __name__ == "__main__":
    main()
