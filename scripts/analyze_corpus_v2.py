"""Aplica a regra de decisão da Fase 21 (ADR-056) à execução única da C6 com o corpus v2.

Referência: a C6 com o corpus v1, da execução única da Fase 20 (`output/v7_runs/final/`), sem
reexecução. Candidata: a C6 com o corpus v2 (`output/corpus_v2_runs/`). Critérios E1–E3 no teste
externo 2 (bootstrap por item da Fase 18), K1–K2 no teste do C7 (bootstrap por família) e O1 nos
dois. Grava um resumo sem texto de alegação nem trechos do corpus, pronto para versionar.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from analyze_v6 import bootstrap_external, external_metrics  # type: ignore[import-not-found]

from immunocheck.evaluation.verdict_v7 import (
    grave_error,
    macro_f1,
    paired_family_bootstrap,
    summarize,
)

REPOSITORY = Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "output/v7_runs/final"
CANDIDATE = REPOSITORY / "output/corpus_v2_runs"
BATCH = REPOSITORY / "corpus/reviews/batch_009.csv"
REPORT = REPOSITORY / "evaluation/corpus_v2/results.json"
SAMPLES = 10_000
INSUFFICIENT = "INSUFFICIENT_EVIDENCE"


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def failure_limit(rate: float) -> float:
    return max(0.02, rate)


def batch_documents() -> set[str]:
    with BATCH.open(encoding="utf-8", newline="") as file:
        return {row["document_id"] for row in csv.DictReader(file)}


def new_source_share(rows: list[dict], documents: set[str]) -> dict:
    """Proporção de respostas e de fontes citadas que vêm do lote 009."""

    cited = [source for row in rows for source in row["source_ids"]]
    from_batch = [source for source in cited if source.split(":", 1)[0] in documents]
    answers = sum(
        any(source.split(":", 1)[0] in documents for source in row["source_ids"]) for row in rows
    )
    return {
        "sources_cited": len(cited),
        "sources_from_batch": len(from_batch),
        "answers_citing_batch": answers,
    }


def coverage_by_topic(rows: list[dict]) -> dict:
    totals, concluded = Counter(), Counter()
    for row in rows:
        topic = row.get("corpus_topic_coverage") or "unknown"
        totals[topic] += 1
        concluded[topic] += row["verdict"] != INSUFFICIENT
    return {topic: {"n": totals[topic], "concluded": concluded[topic]} for topic in sorted(totals)}


def c7_transitions(candidate: list[dict], reference: list[dict]) -> dict:
    """Trocas de veredito entre o corpus v1 e o v2, por rótulo esperado (diagnóstico)."""

    base = {row["case_id"]: row for row in reference}
    changes = Counter(
        f"{row['expected_label']}: {base[row['case_id']]['verdict']} -> {row['verdict']}"
        for row in candidate
        if row["verdict"] != base[row["case_id"]]["verdict"]
    )
    return dict(sorted(changes.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Regra de decisão da Fase 21.")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()

    documents = batch_documents()
    ext_ref = load(REFERENCE / "C6_external2_final.jsonl")
    ext_new = load(CANDIDATE / "C6_external2_corpus_v2.jsonl")
    c7_ref = load(REFERENCE / "C6_c7_final.jsonl")
    c7_new = load(CANDIDATE / "C6_c7_corpus_v2.jsonl")
    if len(ext_new) != len(ext_ref) or len(c7_new) != len(c7_ref):
        raise SystemExit("A execução do corpus v2 está incompleta.")

    ext_base, ext_cand = external_metrics(ext_ref), external_metrics(ext_new)
    ext_delta = bootstrap_external(ext_new, ext_ref)
    c7_base, c7_cand = summarize(c7_ref), summarize(c7_new)
    f1 = paired_family_bootstrap(c7_new, c7_ref, macro_f1, samples=SAMPLES, seed=42)
    grave = paired_family_bootstrap(c7_new, c7_ref, grave_error, samples=SAMPLES, seed=42)

    coverage = ext_delta["coverage"]
    gates = {
        "E1": coverage["delta"] >= 0.03 and coverage["ci95"][0] > 0,
        "E2": ext_delta["conclusive_precision"]["ci95"][0] >= -0.05,
        "E3": ext_cand["severe_error_rate"] - ext_base["severe_error_rate"] <= 0.01,
        "K1": f1["ci_low"] >= -0.05,
        "K2": grave["delta"] <= 0.02,
        "O1": ext_cand["p95_latency_s"] <= 45
        and c7_cand["p95_s"] <= 45
        and ext_cand["failure_rate"] <= failure_limit(ext_base["failure_rate"])
        and c7_cand["failure_rate"] <= failure_limit(c7_base["failure_rate"]),
    }
    keys = (
        "n",
        "conclusive_precision",
        "severe_error_rate",
        "coverage",
        "failure_rate",
        "p95_latency_s",
        "confusion_4class",
    )
    report = {
        "reference": "C6 + corpus v1 (execução única da Fase 20)",
        "candidate": "C6 + corpus v2",
        "external2": {
            "reference": {key: ext_base[key] for key in keys},
            "candidate": {key: ext_cand[key] for key in keys},
            "bootstrap": ext_delta,
            "coverage_by_topic": {
                "reference": coverage_by_topic(ext_ref),
                "candidate": coverage_by_topic(ext_new),
            },
            "batch_009_sources": new_source_share(ext_new, documents),
        },
        "c7": {
            "reference": c7_base,
            "candidate": c7_cand,
            "delta_macro_f1": f1,
            "delta_grave_error": grave,
            "transitions": c7_transitions(c7_new, c7_ref),
            "batch_009_sources": new_source_share(c7_new, documents),
        },
        "gates": gates,
        "adopted": all(gates.values()),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
