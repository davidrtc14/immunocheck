"""Aplica os 8 gates de HOLDOUT_PROTOCOL.md às execuções únicas do holdout v4."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_v4_calibration import (  # type: ignore[import-not-found]
    INSUFFICIENT,
    RESULTS,
    metrics,
    paired_bootstrap,
)


def load_holdout(condition: str) -> list[dict]:
    path = RESULTS / f"holdout_{condition}.jsonl"
    rows = [json.loads(l) for l in path.read_text("utf-8").splitlines() if l]
    if len(rows) != 48:
        raise SystemExit(f"{condition}: {len(rows)} registros; esperados 48.")
    return sorted(rows, key=lambda row: row["item_id"])


def citation_rate(rows: list[dict]) -> float:
    eligible = [r for r in rows if r["expected_label"] != INSUFFICIENT]
    hits = sum(
        r["verdict"] != INSUFFICIENT and bool(set(r["source_ids"]) & set(r["evidence_chunk_ids"]))
        for r in eligible
    )
    return hits / len(eligible)


def abstention_precision(expected: list[str], predicted: list[str]) -> float:
    abstained = [i for i, label in enumerate(predicted) if label == INSUFFICIENT]
    return sum(expected[i] == INSUFFICIENT for i in abstained) / len(abstained) if abstained else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Gates do holdout v4.")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = RESULTS / "holdout_analysis.json"
    if output.exists() and not args.overwrite:
        parser.error("Análise já existe; use --overwrite apenas para reproduzir.")

    base, cand = load_holdout("v3_plain"), load_holdout("v4_candidate")
    expected = [r["expected_label"] for r in base]
    if [r["item_id"] for r in base] != [r["item_id"] for r in cand]:
        raise SystemExit("As condições não cobrem os mesmos itens.")
    families = [r["claim_family"] for r in base]
    base_pred, cand_pred = [r["verdict"] for r in base], [r["verdict"] for r in cand]
    base_m, cand_m = metrics(expected, base_pred, base), metrics(expected, cand_pred, cand)
    bootstrap = paired_bootstrap(expected, base_pred, cand_pred, families)
    confusion = {
        name: {f"{e[:4]}->{p[:4]}": sum(1 for x, y in zip(expected, pred, strict=True) if (x, y) == (e, p))
               for e in sorted(set(expected)) for p in sorted(set(pred))
               if any((x, y) == (e, p) for x, y in zip(expected, pred, strict=True))}
        for name, pred in (("v3_plain", base_pred), ("v4_candidate", cand_pred))
    }
    cand_cit, base_cit = citation_rate(cand), citation_rate(base)
    gates = {
        "1_macro_f1>=0.45": cand_m["macro_f1"] >= 0.45,
        "2_gain_vs_v3>=0.05": cand_m["macro_f1"] - base_m["macro_f1"] >= 0.05,
        "3_abstention_recall>=0.50_and_precision>=0.50": cand_m["recall"][INSUFFICIENT] >= 0.50
        and abstention_precision(expected, cand_pred) >= 0.50,
        "4_conclusion_precision>=v3": cand_m["conclusion_precision"] >= base_m["conclusion_precision"],
        "5_recall_drop_S_R<=0.10": all(
            base_m["recall"][c] - cand_m["recall"][c] <= 0.10 for c in ("SUPPORTED", "REFUTED")
        ),
        "6_failures<=2": cand_m["failures"] <= 2,
        "7_p95<=45s": cand_m["p95_latency_s"] <= 45,
        "8_citation>=0.50_and_not_below_v3-0.05": cand_cit >= 0.50 and cand_cit >= base_cit - 0.05,
    }
    report = {
        "v3_plain": {**base_m, "citation_rate": base_cit,
                     "abstention_precision": abstention_precision(expected, base_pred)},
        "v4_candidate": {**cand_m, "citation_rate": cand_cit,
                         "abstention_precision": abstention_precision(expected, cand_pred)},
        "paired_bootstrap_family_candidate_minus_v3": bootstrap,
        "confusion": confusion,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({k: report[k] for k in ("gates", "all_gates_passed", "paired_bootstrap_family_candidate_minus_v3")}, indent=2))
    for name in ("v3_plain", "v4_candidate"):
        v = report[name]
        print(name, round(v["macro_f1"], 3), {k[:4]: round(x, 2) for k, x in v["recall"].items()},
              "prec", round(v["conclusion_precision"], 3), "cit", round(v["citation_rate"], 3),
              "p95", round(v["p95_latency_s"], 1), "fail", v["failures"])


if __name__ == "__main__":
    main()
