"""Resume execuções da Fase 20 (ADR-054) e compara uma candidata com uma referência.

Uso: `analyze_v7.py <execução.jsonl> [--reference <execução.jsonl>]`. Mostra as métricas do
Adendo 1 (macro-F1, recall por classe, erro grave, falhas, P95) e as diagnósticas (subtipo de
`MISLEADING`, origem do `INSUFFICIENT_EVIDENCE`, chunk de origem entre as fontes).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from immunocheck.evaluation.verdict_v7 import (
    grave_error,
    macro_f1,
    paired_family_bootstrap,
    summarize,
)


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def accuracy_by(rows: list[dict], key: str, label: str) -> dict[str, str]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["expected_label"] == label:
            groups[str(row.get(key))].append(row)
    return {
        name: f"{sum(r['verdict'] == label for r in group)}/{len(group)}"
        for name, group in sorted(groups.items())
    }


def source_hit(rows: list[dict]) -> str:
    corpus = [r for r in rows if r.get("origin_type") == "corpus_chunk"]
    hits = sum(r["source_chunk_id"] in (r.get("source_ids") or []) for r in corpus)
    return f"{hits}/{len(corpus)}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise da Fase 20 (ADR-054).")
    parser.add_argument("run", type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--samples", type=int, default=10_000)
    args = parser.parse_args()

    rows = load(args.run)
    report: dict[str, object] = {
        "run": args.run.name,
        **summarize(rows),
        "misleading_by_subtype": accuracy_by(rows, "misleading_subtype", "MISLEADING"),
        "insufficient_by_origin": accuracy_by(rows, "origin_type", "INSUFFICIENT_EVIDENCE"),
        "source_chunk_in_sources": source_hit(rows),
        "failures": sorted({str(r["failure"]) for r in rows if r.get("failure")}),
    }
    if args.reference:
        reference = load(args.reference)
        report["reference"] = args.reference.name
        report["delta_macro_f1"] = {
            k: round(v, 4)
            for k, v in paired_family_bootstrap(
                rows, reference, macro_f1, samples=args.samples
            ).items()
        }
        report["delta_grave_error"] = round(grave_error(rows) - grave_error(reference), 4)
        changed = {r["case_id"] for r in rows} & {
            r["case_id"]
            for r in reference
            if r["verdict"] != next(x for x in rows if x["case_id"] == r["case_id"])["verdict"]
        }
        report["changed_verdicts"] = len(changed)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
