"""Analisa a calibração D1/D2 conforme CALIBRATION_D_PLAN.md e grava thresholds.json."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from sklearn.metrics import f1_score, precision_recall_fscore_support

from immunocheck.application.abstention import (
    LABELS,
    AbstentionThresholds,
    CalibrationRecord,
    RunSignals,
    _apply,
    abstention_curve,
    calibrate_thresholds,
)

REPOSITORY = Path(__file__).resolve().parents[1]
RESULTS = REPOSITORY / "evaluation/refinement_v4/results"
THRESHOLDS = REPOSITORY / "evaluation/refinement_v4/thresholds.json"
INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 20261013


def load(condition: str) -> list[dict]:
    path = RESULTS / f"calibration_{condition}.jsonl"
    rows = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]
    if len(rows) != 48:
        raise SystemExit(f"{condition}: {len(rows)} registros; esperados 48.")
    return sorted(rows, key=lambda row: row["item_id"])


def to_records(rows: list[dict]) -> list[CalibrationRecord]:
    empty = RunSignals(None, None, None, 0)
    return [
        CalibrationRecord(
            row["expected_label"],
            row["verdict"],
            RunSignals(**row["signals"]) if row["signals"] else empty,
        )
        for row in rows
    ]


def macro_f1(expected: list[str], predicted: list[str]) -> float:
    return float(f1_score(expected, predicted, labels=LABELS, average="macro", zero_division=0))


def metrics(expected: list[str], predicted: list[str], rows: list[dict]) -> dict:
    precision, recall, _, _ = precision_recall_fscore_support(
        expected, predicted, labels=LABELS, zero_division=0
    )
    conclusive = [i for i, label in enumerate(predicted) if label != INSUFFICIENT]
    latencies = sorted(row["latency_ms"] for row in rows)
    return {
        "macro_f1": macro_f1(expected, predicted),
        "recall": dict(zip(LABELS, map(float, recall), strict=True)),
        "precision": dict(zip(LABELS, map(float, precision), strict=True)),
        "conclusion_precision": (
            sum(expected[i] == predicted[i] for i in conclusive) / len(conclusive)
            if conclusive
            else 0.0
        ),
        "conclusions": len(conclusive),
        "failures": sum(row["failure"] is not None for row in rows),
        "median_latency_s": statistics.median(latencies) / 1000,
        "p95_latency_s": latencies[int(0.95 * (len(latencies) - 1))] / 1000,
    }


def paired_bootstrap(expected, before, after, families) -> dict:
    by_family: dict[str, list[int]] = defaultdict(list)
    for index, family in enumerate(families):
        by_family[family].append(index)
    names = sorted(by_family)
    rng = random.Random(BOOTSTRAP_SEED)
    deltas = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [i for f in rng.choices(names, k=len(names)) for i in by_family[f]]
        exp = [expected[i] for i in sample]
        deltas.append(
            macro_f1(exp, [after[i] for i in sample]) - macro_f1(exp, [before[i] for i in sample])
        )
    deltas.sort()
    return {
        "delta": macro_f1(expected, after) - macro_f1(expected, before),
        "lower": deltas[int(0.025 * len(deltas))],
        "upper": deltas[int(0.975 * len(deltas)) - 1],
    }


def nested_lofo(rows: list[dict]) -> dict:
    """Deixa cada família de fora: calibra nas demais e aplica à família retida."""
    records = to_records(rows)
    families = [row["claim_family"] for row in rows]
    final = [""] * len(rows)
    for held in sorted(set(families)):
        train = [r for r, f in zip(records, families, strict=True) if f != held]
        thresholds, _ = calibrate_thresholds(train)
        for index, family in enumerate(families):
            if family == held:
                final[index] = _apply(records[index], thresholds)
    expected = [row["expected_label"] for row in rows]
    return {"predictions": final, "macro_f1": macro_f1(expected, final)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise D1/D2 na calibração v4.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = RESULTS / "calibration_d_analysis.json"
    if output.exists() and not args.overwrite:
        parser.error("Análise já existe; use --overwrite para reproduzir.")

    plain, grounded = load("v3_plain"), load("v4_grounded")
    expected = [row["expected_label"] for row in plain]
    families = [row["claim_family"] for row in plain]
    if [r["item_id"] for r in plain] != [r["item_id"] for r in grounded]:
        raise SystemExit("As condições não cobrem os mesmos itens.")

    report: dict = {"conditions": {}, "decisions": {}}
    predictions = {}
    for name, rows in (("v3_plain", plain), ("v4_grounded", grounded)):
        predicted = [row["verdict"] for row in rows]
        predictions[name] = predicted
        thresholds, info = calibrate_thresholds(to_records(rows))
        nested = nested_lofo(rows)
        report["conditions"][name] = {
            **metrics(expected, predicted, rows),
            "in_sample_threshold": {"thresholds": asdict(thresholds), **info},
            "abstention_curve_in_sample": abstention_curve(to_records(rows), thresholds),
            "nested_lofo_macro_f1": nested["macro_f1"],
            "nested_lofo_delta_vs_no_threshold": nested["macro_f1"] - macro_f1(expected, predicted),
        }
        predictions[name + "+lofo"] = nested["predictions"]

    plain_m, grounded_m = report["conditions"]["v3_plain"], report["conditions"]["v4_grounded"]
    d1 = {
        "macro_f1_non_inferior": grounded_m["macro_f1"] >= plain_m["macro_f1"] - 0.03,
        "precision_or_f1_gain": (
            grounded_m["conclusion_precision"] >= plain_m["conclusion_precision"] + 0.05
            or grounded_m["macro_f1"] > plain_m["macro_f1"]
        ),
        "failures_and_latency": grounded_m["failures"] <= 0.02 * 48
        and grounded_m["p95_latency_s"] <= 45,
        "paired_bootstrap_family": paired_bootstrap(
            expected, predictions["v3_plain"], predictions["v4_grounded"], families
        ),
    }
    d1["adopted"] = all(d1[k] for k in ("macro_f1_non_inferior", "precision_or_f1_gain", "failures_and_latency"))
    base = "v4_grounded" if d1["adopted"] else "v3_plain"
    d2 = {
        "base_condition": base,
        "nested_delta": report["conditions"][base]["nested_lofo_delta_vs_no_threshold"],
        "adopted": report["conditions"][base]["nested_lofo_delta_vs_no_threshold"] >= 0.03,
        "paired_bootstrap_family": paired_bootstrap(
            expected, predictions[base], predictions[base + "+lofo"], families
        ),
    }
    report["decisions"] = {"D1": d1, "D2": d2}

    if d2["adopted"]:
        rows = grounded if base == "v4_grounded" else plain
        thresholds, info = calibrate_thresholds(to_records(rows))
        THRESHOLDS.write_text(
            json.dumps(
                {
                    "base_condition": base,
                    "frozen_from": "calibration_v4_development_48_items",
                    "thresholds": asdict(thresholds),
                    "calibration": info,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    elif THRESHOLDS.exists():
        THRESHOLDS.unlink()
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({k: v for k, v in report["decisions"].items()}, indent=2, ensure_ascii=False))
    for name, value in report["conditions"].items():
        print(name, round(value["macro_f1"], 3), "lofo", round(value["nested_lofo_macro_f1"], 3))


if __name__ == "__main__":
    main()
