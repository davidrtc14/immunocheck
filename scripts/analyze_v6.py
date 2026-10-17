"""Analisa a Fase 18 (ADR-051): critérios v4 e gates do teste externo contra a v3.

As métricas e a regra seguem `evaluation/refinement_v6/PROTOCOL.md` e o Adendo 1. No v4, a v3 de
referência é a da linha v5 (`refinement_v5/results/dev/v3_all_run1.jsonl`). No teste externo, a
v3 é executada nesta fase.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from analyze_v4_calibration import paired_bootstrap  # type: ignore[import-not-found]
from analyze_v5 import (  # type: ignore[import-not-found]
    RESULTS as V5_RESULTS,
)
from analyze_v5 import (
    by_form,
    gates,
    load_rows,
    summarize,
    three_class_f1,
)

from immunocheck.evaluation.paraphrase_set import ORIGINAL_FORM

REPOSITORY = Path(__file__).resolve().parents[1]
RESULTS = REPOSITORY / "evaluation/refinement_v6/results"
BOOTSTRAP_SAMPLES = 10_000
SUPPORTED, INSUFFICIENT = "SUPPORTED", "INSUFFICIENT_EVIDENCE"


def binary(label: str) -> str | None:
    """Sustentada, não sustentada ou abstenção (None)."""

    if label == INSUFFICIENT:
        return None
    return "sustentada" if label == SUPPORTED else "nao_sustentada"


def external_metrics(rows: list[dict]) -> dict:
    conclusive = [row for row in rows if binary(row["verdict"]) is not None]
    correct = [row for row in conclusive if binary(row["verdict"]) == binary(row["expected_label"])]
    not_supported = [row for row in rows if row["expected_label"] != SUPPORTED]
    severe = [row for row in not_supported if row["verdict"] == SUPPORTED]
    latencies = sorted(row["latency_ms"] / 1000 for row in rows)
    supported = [row for row in rows if row["expected_label"] == SUPPORTED]
    covered = [row for row in rows if row.get("corpus_topic_coverage") == "covered"]
    strata: dict[str, dict] = {}
    for key in ("corpus_topic_coverage", "external_source"):
        for value in sorted({str(row.get(key)) for row in rows}):
            group = [row for row in rows if str(row.get(key)) == value]
            group_conclusive = [row for row in group if binary(row["verdict"]) is not None]
            strata[f"{key}={value}"] = {
                "n": len(group),
                "coverage": len(group_conclusive) / len(group),
                "conclusive_precision": (
                    sum(
                        binary(r["verdict"]) == binary(r["expected_label"])
                        for r in group_conclusive
                    )
                    / len(group_conclusive)
                    if group_conclusive
                    else None
                ),
            }
    individual = [
        row for row in rows if "possible_individual_event" in row.get("external_flags", [])
    ]
    return {
        "n": len(rows),
        "conclusive_precision": len(correct) / len(conclusive) if conclusive else None,
        "severe_error_rate": len(severe) / len(not_supported) if not_supported else None,
        "coverage": len(conclusive) / len(rows),
        "failures": sum(row["failure"] is not None for row in rows),
        "failure_rate": sum(row["failure"] is not None for row in rows) / len(rows),
        "p95_latency_s": latencies[max(0, round(0.95 * len(latencies)) - 1)],
        "supported_recall_descriptive": (
            sum(row["verdict"] == SUPPORTED for row in supported) / len(supported)
            if supported
            else None
        ),
        "macro_f1_3class_covered": three_class_f1(
            [row["expected_label"] for row in covered], [row["verdict"] for row in covered]
        )
        if covered
        else None,
        "individual_event_verdicts": dict(Counter(row["verdict"] for row in individual)),
        "confusion_4class": dict(Counter(f"{r['expected_label']}->{r['verdict']}" for r in rows)),
        "strata": strata,
    }


def bootstrap_external(candidate: list[dict], baseline: list[dict], seed: int = 42) -> dict:
    """Diferenças de precisão das conclusões, erro grave e cobertura, reamostrando itens."""

    base = {row["case_id"]: row for row in baseline}
    pairs = [(row, base[row["case_id"]]) for row in candidate if row["case_id"] in base]

    def deltas(sample: list[tuple[dict, dict]]) -> tuple[float, float, float]:
        cand = external_metrics([c for c, _ in sample])
        ref = external_metrics([b for _, b in sample])

        def diff(key: str) -> float:
            return (cand[key] or 0.0) - (ref[key] or 0.0)

        return diff("conclusive_precision"), diff("severe_error_rate"), diff("coverage")

    rng = random.Random(seed)
    draws = [deltas([rng.choice(pairs) for _ in pairs]) for _ in range(BOOTSTRAP_SAMPLES)]
    point = deltas(pairs)
    result = {}
    for index, name in enumerate(("conclusive_precision", "severe_error_rate", "coverage")):
        ordered = sorted(draw[index] for draw in draws)
        result[name] = {
            "delta": round(point[index], 4),
            "ci95": [
                round(ordered[int(0.025 * len(ordered))], 4),
                round(ordered[int(0.975 * len(ordered)) - 1], 4),
            ],
        }
    return result


def external_gates(candidate: dict, baseline: dict, bootstrap: dict) -> dict[str, bool]:
    precision = bootstrap["conclusive_precision"]
    return {
        "X1_precision_non_inferior": precision["delta"] >= -0.02 and precision["ci95"][0] >= -0.08,
        "X2_severe_error": candidate["severe_error_rate"] <= baseline["severe_error_rate"] + 0.02,
        "X3_coverage_drop_le_0.10": baseline["coverage"] - candidate["coverage"] <= 0.10,
        "X4_failures_and_latency": candidate["failure_rate"] <= 0.02
        and candidate["p95_latency_s"] <= 45,
    }


def v4_report(name: str, phase: str) -> dict:
    """Critérios v5 nos 96 itens; o 3 fica descritivo (Adendo 1)."""

    baseline_rows = load_rows(V5_RESULTS / "dev" / "v3_all_run1.jsonl", "all")
    baseline = summarize(baseline_rows)
    rows = load_rows(RESULTS / phase / f"{name}.jsonl", "all")
    summary = summarize(rows)
    original, base_original = by_form(rows)[ORIGINAL_FORM], by_form(baseline_rows)[ORIGINAL_FORM]
    if [r["parent_item_id"] for r in original] != [r["parent_item_id"] for r in base_original]:
        return {"summary": summary, "gates": None}
    summary["bootstrap_vs_v3"] = paired_bootstrap(
        [r["expected_label"] for r in original],
        [r["verdict"] for r in base_original],
        [r["verdict"] for r in original],
        [r["claim_family"] for r in original],
    )
    criteria = gates(summary, baseline, summary["bootstrap_vs_v3"])
    descriptive = criteria.pop("3_recall_drop_s_r_le_0.10")
    return {"summary": summary, "gates": criteria, "criterion_3_descriptive": descriptive}


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise da Fase 18.")
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--external", nargs="*", default=[], help="condições no teste externo")
    parser.add_argument("--v4", nargs="*", default=[], help="ex.: v5_fixed_v4_all_run1")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report: dict = {"phase": args.phase, "v4": {}, "external": {}}
    for name in args.v4:
        report["v4"][name] = v4_report(name, args.phase)
    if args.external:
        data = {
            name: load_rows(RESULTS / args.phase / f"{name}_external_all_run1.jsonl", "all")
            for name in args.external
        }
        metrics = {name: external_metrics(rows) for name, rows in data.items()}
        for name, rows in data.items():
            entry: dict = {"metrics": metrics[name]}
            if name != "v3" and "v3" in data:
                entry["bootstrap_vs_v3"] = bootstrap_external(rows, data["v3"])
                entry["gates"] = external_gates(
                    metrics[name], metrics["v3"], entry["bootstrap_vs_v3"]
                )
            report["external"][name] = entry
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
