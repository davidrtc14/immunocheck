"""Analisa a linha de base sem recuperação (ADR-058) e reanalisa as conclusões do teste externo 2.

Lê os registros da execução única da Fase 20 (`output/v7_runs/final/`, v3 e C6 = v7) e os da linha
de base (`output/no_rag_runs/`). No teste do C7: macro-F1, erro grave, recall por classe e diferenças
v7 − sem RAG com bootstrap pareado por família. No teste externo 2: as métricas da Fase 18, a acurácia
exata nas conclusões (quatro classes) por classe do gabarito, a comparação com o classificador trivial
que responde "refutada" para tudo e as diferenças v7 − sem RAG com bootstrap por item. Grava um resumo
sem texto de alegação, explicação nem trecho do corpus.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from analyze_v6 import bootstrap_external, external_metrics  # type: ignore[import-not-found]

from immunocheck.evaluation.verdict_v7 import (
    LABELS,
    grave_error,
    macro_f1,
    paired_family_bootstrap,
    summarize,
)

REPOSITORY = Path(__file__).resolve().parents[1]
V7_RUNS = REPOSITORY / "output/v7_runs/final"
NO_RAG_RUNS = REPOSITORY / "output/no_rag_runs"
REPORT = REPOSITORY / "evaluation/no_rag/results.json"
SAMPLES = 10_000
INSUFFICIENT = "INSUFFICIENT_EVIDENCE"


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def load(condition: str, dataset: str) -> list[dict]:
    if condition == "no_rag":
        return _read(NO_RAG_RUNS / f"no_rag_{dataset}.jsonl")
    return _read(V7_RUNS / f"{condition}_{dataset}_final.jsonl")


def conclusions(rows: list[dict]) -> dict:
    """Acurácia exata (quatro classes) entre as respostas conclusivas, geral e por classe."""

    conclusive = [row for row in rows if row["verdict"] != INSUFFICIENT]
    by_label = {}
    for label in LABELS:
        group = [row for row in conclusive if row["expected_label"] == label]
        if group:
            by_label[label] = {
                "n_conclusive": len(group),
                "exact_accuracy": round(sum(r["verdict"] == label for r in group) / len(group), 4),
            }
    return {
        "n_conclusive": len(conclusive),
        "exact_accuracy": round(
            sum(r["verdict"] == r["expected_label"] for r in conclusive) / len(conclusive), 4
        )
        if conclusive
        else None,
        "by_expected_label": by_label,
        "confusion": dict(
            Counter(f"{r['expected_label']}->{r['verdict']}" for r in rows).most_common()
        ),
    }


def trivial(rows: list[dict], label: str) -> list[dict]:
    return [dict(row, verdict=label, failure=None, latency_ms=0.0) for row in rows]


def external_summary(rows: list[dict]) -> dict:
    metrics = external_metrics(rows)
    return {
        **{
            key: metrics[key]
            for key in (
                "n",
                "conclusive_precision",
                "severe_error_rate",
                "coverage",
                "failure_rate",
            )
        },
        "conclusions": conclusions(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Linha de base sem recuperação (ADR-058).")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()

    report: dict[str, dict] = {"c7": {}, "external2": {}}
    c7 = {name: load(name, "c7") for name in ("v3", "C6", "no_rag")}
    majority = Counter(row["expected_label"] for row in c7["C6"]).most_common(1)[0][0]
    for name, rows in c7.items():
        report["c7"][name] = {**summarize(rows), "conclusions": conclusions(rows)}
    report["c7"][f"trivial_{majority}"] = summarize(trivial(c7["C6"], majority))
    report["c7"]["C6_minus_no_rag"] = {
        "macro_f1": paired_family_bootstrap(
            c7["C6"], c7["no_rag"], macro_f1, samples=SAMPLES, seed=42
        ),
        "grave_error": paired_family_bootstrap(
            c7["C6"], c7["no_rag"], grave_error, samples=SAMPLES, seed=42
        ),
    }

    ext = {name: load(name, "external2") for name in ("v3", "C6", "no_rag")}
    for name, rows in ext.items():
        report["external2"][name] = external_summary(rows)
    report["external2"]["trivial_REFUTED"] = external_summary(trivial(ext["C6"], "REFUTED"))
    report["external2"]["C6_minus_no_rag"] = bootstrap_external(ext["C6"], ext["no_rag"])

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
