"""Aplica os critérios de CALIBRATION_D4_PLAN.md à condição v4_d4 contra v4_grounded."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from analyze_v4_calibration import (  # type: ignore[import-not-found]
    INSUFFICIENT,
    RESULTS,
    load,
    metrics,
    paired_bootstrap,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise D4/D5 na calibração v4.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = RESULTS / "calibration_d4_analysis.json"
    if output.exists() and not args.overwrite:
        parser.error("Análise já existe; use --overwrite para reproduzir.")

    base, d4 = load("v4_grounded"), load("v4_d4")
    expected = [row["expected_label"] for row in base]
    families = [row["claim_family"] for row in base]
    base_m = metrics(expected, [r["verdict"] for r in base], base)
    d4_m = metrics(expected, [r["verdict"] for r in d4], d4)

    routes: dict[str, Counter] = {}
    for row in d4:
        routes.setdefault(row["expected_label"], Counter())[row.get("route") or "none"] += 1
    technical = sum(bool(row.get("technical_abstention")) for row in d4)
    unhandled = sum(row["failure"] is not None for row in d4)

    gates = {
        "misleading_recall>=0.33": d4_m["recall"]["MISLEADING"] >= 4 / 12,
        "macro_f1>=base+0.03": d4_m["macro_f1"] >= base_m["macro_f1"] + 0.03,
        "conclusion_precision>=base-0.05": d4_m["conclusion_precision"]
        >= base_m["conclusion_precision"] - 0.05,
        "abstention_recall>=0.60": d4_m["recall"][INSUFFICIENT] >= 0.60,
        "no_unhandled_exception": unhandled == 0,
        "p95<=45s": d4_m["p95_latency_s"] <= 45,
    }
    report = {
        "v4_grounded": base_m,
        "v4_d4": d4_m,
        "paired_bootstrap_family_d4_minus_grounded": paired_bootstrap(
            expected, [r["verdict"] for r in base], [r["verdict"] for r in d4], families
        ),
        "routes_by_expected_label": {k: dict(v) for k, v in routes.items()},
        "technical_abstentions": technical,
        "unhandled_exceptions": unhandled,
        "gates": gates,
        "adopted": all(gates.values()),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({k: report[k] for k in ("gates", "adopted", "routes_by_expected_label")}, indent=2))
    for name in ("v4_grounded", "v4_d4"):
        value = report[name]
        print(name, round(value["macro_f1"], 3), {k[:4]: round(v, 2) for k, v in value["recall"].items()},
              round(value["conclusion_precision"], 3), round(value["p95_latency_s"], 1))
    print(report["paired_bootstrap_family_d4_minus_grounded"])


if __name__ == "__main__":
    main()
