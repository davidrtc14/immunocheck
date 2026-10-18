"""Executa uma condição da Fase 20 (ADR-054) no C7 ou no teste externo 2.

Fase `dev`: só o split de desenvolvimento do C7, livre para iterar (Adendo 1 do protocolo).
Fase `final`: execução única no teste do C7 e no teste externo 2; exige o congelamento da v7 em
`evaluation/refinement_v7/verdict_freeze.json` (ainda não implementada).
Os registros são checkpoints JSONL retomáveis, fora do Git em `output/v7_runs/`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_v6_experiment import build_pipeline as build_v6_pipeline  # type: ignore[import-not-found]

from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict

REPOSITORY = Path(__file__).resolve().parents[1]
C7_ITEMS = REPOSITORY / "evaluation/refinement_v7/items.jsonl"
RUNS = REPOSITORY / "output/v7_runs"
CONDITIONS = ("v3", "v5_fixed")


def c7_cases(split: str) -> list[dict]:
    rows = [json.loads(line) for line in C7_ITEMS.read_text("utf-8").splitlines() if line]
    return [
        {
            "case_id": row["item_id"],
            "claim": row["claim"],
            "claim_family": row["claim_family"],
            "expected_label": row["label"],
            "split": row["split"],
            "origin_type": row["origin_type"],
            "misleading_subtype": row["misleading_subtype"],
            "source_chunk_id": row["source_chunk_id"],
        }
        for row in rows
        if row["split"] == split
    ]


def build_pipeline(condition: str, trace_sink):
    return build_v6_pipeline(condition, trace_sink)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimento v7 (ADR-054).")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--phase", choices=("dev",), default="dev")
    parser.add_argument("--limit", type=int, help="só os primeiros N casos")
    parser.add_argument("--tag", default="run1")
    args = parser.parse_args()

    cases = c7_cases("development")
    if args.limit:
        cases = cases[: args.limit]
    output_dir = RUNS / args.phase
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / f"{args.condition}_c7_development_{args.tag}.jsonl"
    done: set[str] = set()
    if checkpoint.exists():
        done = {
            json.loads(line)["case_id"]
            for line in checkpoint.read_text("utf-8").splitlines()
            if line
        }

    traces: list[dict] = []
    pipeline = build_pipeline(args.condition, traces.append)
    with checkpoint.open("a", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            if case["case_id"] in done:
                continue
            traces.clear()
            started = time.perf_counter()
            failure = None
            try:
                result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=case["claim"]))
                verdict = result.verdict.value
                source_ids = [source.chunk_id for source in result.sources]
            except Exception as exc:  # noqa: BLE001 - falha técnica é dado do experimento
                verdict = Verdict.INSUFFICIENT_EVIDENCE.value
                source_ids, failure = [], type(exc).__name__
            trace = traces[-1] if traces else None
            if trace and trace.get("technical_abstention") and failure is None:
                failure = "TechnicalAbstention"
            record = {key: value for key, value in case.items() if key != "claim"}
            record.update(
                verdict=verdict,
                source_ids=source_ids,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                failure=failure,
                trace=trace,
            )
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(case["case_id"], "->", verdict, failure or "", flush=True)


if __name__ == "__main__":
    main()
