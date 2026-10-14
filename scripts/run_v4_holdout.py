"""Executa o holdout v4 (split test) uma única vez por condição, após verificar o congelamento."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from freeze_v4_candidate import FREEZE, current_hashes, ollama_digest  # type: ignore[import-not-found]

from immunocheck.application.abstention import AbstentionThresholds
from immunocheck.bootstrap import build_v4_text_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict
from immunocheck.evaluation.end_to_end import DatasetSplit, load_end_to_end_items

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
OUTPUT_DIR = REPOSITORY / "evaluation/refinement_v4/results"
CONDITIONS = {
    "v3_plain": {"grounded": False, "d4": False},
    "v4_candidate": {"grounded": True, "d4": False},
}


def verify_freeze() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    changed = [n for n, h in current_hashes().items() if freeze["sha256"].get(n) != h]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))
    if ollama_digest() != freeze["ollama_digest"]:
        raise SystemExit("O digest do modelo difere do congelado.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Holdout v4: execução única por condição.")
    parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    args = parser.parse_args()
    verify_freeze()

    items = sorted(
        (i for i in load_end_to_end_items(ITEMS, require_reviewed=True) if i.split is DatasetSplit.TEST),
        key=lambda item: item.item_id,
    )
    if len(items) != 48:
        raise SystemExit("O holdout deve ter 48 itens.")
    checkpoint = OUTPUT_DIR / f"holdout_{args.condition}.jsonl"
    done = set()
    if checkpoint.exists():
        done = {json.loads(l)["item_id"] for l in checkpoint.read_text("utf-8").splitlines() if l}
        if len(done) == 48:
            raise SystemExit("Esta condição já foi executada; o holdout não se repete.")

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
            signals = pipeline.last_signals
            record = {
                "item_id": item.item_id,
                "claim_family": item.claim_family,
                "expected_label": item.label.value,
                "evidence_chunk_ids": list(item.evidence_chunk_ids),
                "verdict": verdict,
                "source_ids": source_ids,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "failure": failure,
                "signals": asdict(signals) if signals else None,
                "route": pipeline.last_route,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(item.item_id, "->", verdict, failure or "")


if __name__ == "__main__":
    main()
