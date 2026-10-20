"""Aplica a regra de promoção da Fase 20 à execução única (Adendos 1 e 3 do protocolo da v7).

Lê `output/v7_runs/final/<condição>_<conjunto>_final.jsonl` para v3, `v5_fixed` e C6 e compara cada
uma com a v3. No teste do C7: P1–P4 (Adendo 1) e, só para a C6, S1–S4 (Adendo 3), com bootstrap
pareado por família. No teste externo 2: X1–X4, com as métricas e o bootstrap por item da Fase 18;
o X4 usa o limite do protocolo da v7, falhas ≤ max(2%, taxa da v3). Grava um resumo sem texto de
alegação nem trechos do corpus, pronto para versionar.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_v6 import bootstrap_external, external_metrics  # type: ignore[import-not-found]

from immunocheck.evaluation.verdict_v7 import (
    grave_error,
    macro_f1,
    paired_family_bootstrap,
    recall_by_label,
    summarize,
)

REPOSITORY = Path(__file__).resolve().parents[1]
FINAL = REPOSITORY / "output/v7_runs/final"
REPORT = REPOSITORY / "evaluation/refinement_v7/results_final.json"
CANDIDATES = ("v5_fixed", "C6")
SAMPLES = 10_000
MISLEADING = "MISLEADING"


def load(condition: str, dataset: str) -> list[dict]:
    path = FINAL / f"{condition}_{dataset}_final.jsonl"
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def failure_limit(baseline: dict) -> float:
    return max(0.02, baseline["failure_rate"])


def c7_gates(candidate: list[dict], baseline: list[dict]) -> dict:
    cand, base = summarize(candidate), summarize(baseline)
    f1 = paired_family_bootstrap(candidate, baseline, macro_f1, samples=SAMPLES, seed=42)
    grave = paired_family_bootstrap(candidate, baseline, grave_error, samples=SAMPLES, seed=42)
    misleading_ok = recall_by_label(candidate)[MISLEADING] >= recall_by_label(baseline)[MISLEADING]
    operational = cand["p95_s"] <= 45 and cand["failure_rate"] <= failure_limit(base)
    return {
        "summary": cand,
        "delta_macro_f1": f1,
        "delta_grave_error": grave,
        "P": {
            "P1": f1["delta"] >= 0.05 and f1["ci_low"] > 0,
            "P2": cand["grave_error"] <= base["grave_error"] + 0.02,
            "P3": misleading_ok,
            "P4": operational,
        },
        "S": {
            "S1": f1["delta"] >= 0 and f1["ci_low"] >= -0.05,
            "S2": grave["delta"] <= -0.03 and grave["ci_high"] < 0,
            "S3": misleading_ok,
            "S4": operational,
        },
    }


def external_gates(candidate: list[dict], baseline: list[dict]) -> dict:
    cand, base = external_metrics(candidate), external_metrics(baseline)
    deltas = bootstrap_external(candidate, baseline)
    precision = deltas["conclusive_precision"]
    return {
        "summary": {
            key: cand[key]
            for key in (
                "n",
                "conclusive_precision",
                "severe_error_rate",
                "coverage",
                "failure_rate",
                "p95_latency_s",
                "confusion_4class",
            )
        },
        "bootstrap": deltas,
        "X": {
            "X1": precision["delta"] >= -0.02 and precision["ci95"][0] >= -0.08,
            "X2": cand["severe_error_rate"] <= base["severe_error_rate"] + 0.02,
            "X3": base["coverage"] - cand["coverage"] <= 0.10,
            "X4": cand["failure_rate"] <= failure_limit(base) and cand["p95_latency_s"] <= 45,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Regra de promoção da Fase 20.")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()

    c7_base, ext_base = load("v3", "c7"), load("v3", "external2")
    report: dict[str, object] = {
        "v3": {"c7": summarize(c7_base), "external2": external_metrics(ext_base)},
    }
    for name in CANDIDATES:
        c7 = c7_gates(load(name, "c7"), c7_base)
        ext = external_gates(load(name, "external2"), ext_base)
        x_ok = all(ext["X"].values())
        by_rule = all(c7["P"].values()) and x_ok
        by_safety = name == "C6" and all(c7["S"].values()) and x_ok
        report[name] = {
            "c7": c7,
            "external2": ext,
            # A `v5_fixed` só é comparação (Adendo 1): nunca é promovida.
            "promoted": name != "v5_fixed" and (by_rule or by_safety),
            "promotion_route": None
            if name == "v5_fixed"
            else "P1-P4"
            if by_rule
            else "S1-S4"
            if by_safety
            else None,
        }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
