"""Analisa condições da linha v5 contra a v3: macro-F1, consistência sob paráfrase, gates.

As métricas seguem `evaluation/refinement_v5/PROTOCOL.md`. A v3 de referência vem sempre da
execução `dev/v3_all_run1.jsonl` (v3 congelada), filtrada ao mesmo split.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from analyze_v4_calibration import (  # type: ignore[import-not-found]
    INSUFFICIENT,
    macro_f1,
    metrics,
    paired_bootstrap,
)
from sklearn.metrics import f1_score

from immunocheck.evaluation.paraphrase_set import ORIGINAL_FORM, PARAPHRASE_STYLES, consistency_rate

REPOSITORY = Path(__file__).resolve().parents[1]
RESULTS = REPOSITORY / "evaluation/refinement_v5/results"
V4_RESULTS = REPOSITORY / "evaluation/refinement_v4/results"
FORMS = (ORIGINAL_FORM, *PARAPHRASE_STYLES)
NOT_SUPPORTED = "NOT_SUPPORTED"


def load_rows(path: Path, split: str) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]
    if split != "all":
        rows = [row for row in rows if row["split"] == split]
    return sorted(rows, key=lambda row: row["case_id"])


def three_class_f1(expected: list[str], predicted: list[str]) -> float:
    def collapse(label: str) -> str:
        return NOT_SUPPORTED if label in {"REFUTED", "MISLEADING"} else label

    labels = ["SUPPORTED", NOT_SUPPORTED, INSUFFICIENT]
    return float(
        f1_score(
            [collapse(x) for x in expected],
            [collapse(x) for x in predicted],
            labels=labels,
            average="macro",
            zero_division=0,
        )
    )


def by_form(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["form"]].append(row)
    return {
        form: sorted(items, key=lambda r: r["parent_item_id"]) for form, items in grouped.items()
    }


def consistency(rows: list[dict]) -> float | None:
    predictions: dict[str, dict[str, str | None]] = defaultdict(dict)
    for row in rows:
        predictions[row["parent_item_id"]][row["form"]] = None if row["failure"] else row["verdict"]
    complete = {k: v for k, v in predictions.items() if set(v) == set(FORMS)}
    return consistency_rate(complete) if complete else None


def abstention(expected: list[str], predicted: list[str]) -> dict[str, float]:
    abstained = [i for i, label in enumerate(predicted) if label == INSUFFICIENT]
    actual = [i for i, label in enumerate(expected) if label == INSUFFICIENT]
    hits = sum(expected[i] == INSUFFICIENT for i in abstained)
    return {
        "precision": hits / len(abstained) if abstained else 0.0,
        "recall": hits / len(actual) if actual else 0.0,
    }


def confusion(expected: list[str], predicted: list[str]) -> dict[str, int]:
    counts = Counter(f"{e[:4]}->{p[:4]}" for e, p in zip(expected, predicted, strict=True))
    return dict(sorted(counts.items()))


def summarize(rows: list[dict]) -> dict:
    forms = by_form(rows)
    summary: dict = {"forms": {}, "consistency": consistency(rows)}
    for form, items in forms.items():
        expected = [r["expected_label"] for r in items]
        predicted = [r["verdict"] for r in items]
        result = metrics(expected, predicted, items)
        result.update(
            macro_f1_3class=three_class_f1(expected, predicted),
            abstention=abstention(expected, predicted),
            confusion=confusion(expected, predicted),
            n=len(items),
        )
        summary["forms"][form] = result
    pooled_expected = [r["expected_label"] for r in rows]
    pooled_predicted = [r["verdict"] for r in rows]
    summary["pooled_macro_f1"] = macro_f1(pooled_expected, pooled_predicted)
    traces = [r["trace"] for r in rows if r.get("trace")]
    if traces:
        summary["claim_kinds"] = dict(Counter(t.get("claim_kind") for t in traces))
        summary["proposition_counts"] = dict(
            Counter(len(t.get("propositions") or []) for t in traces)
        )
        summary["downgrades"] = dict(
            Counter(
                j["downgrade_reason"]
                for t in traces
                for j in t.get("judgments") or []
                if j["downgrade_reason"]
            )
        )
    return summary


def run_stability(first: list[dict], second: dict[str, str]) -> float | None:
    pairs = [
        (r["verdict"], second[r["parent_item_id"]]) for r in first if r["parent_item_id"] in second
    ]
    return sum(a == b for a, b in pairs) / len(pairs) if pairs else None


def v4_stored_v3() -> dict[str, str]:
    stored: dict[str, str] = {}
    for name in ("calibration_v3_plain.jsonl", "holdout_v3_plain.jsonl"):
        for line in (V4_RESULTS / name).read_text("utf-8").splitlines():
            if line:
                row = json.loads(line)
                stored[row["item_id"]] = row["verdict"]
    return stored


def gates(candidate: dict, baseline: dict, bootstrap: dict) -> dict[str, bool]:
    cand, base = candidate["forms"][ORIGINAL_FORM], baseline["forms"][ORIGINAL_FORM]
    return {
        "1_delta_macro_f1_ge_0.05_and_ci_lower_gt_0": bootstrap["delta"] >= 0.05
        and bootstrap["lower"] > 0,
        "2_consistency_ge_v3": (candidate["consistency"] or 0) >= (baseline["consistency"] or 0),
        "3_recall_drop_s_r_le_0.10": all(
            base["recall"][label] - cand["recall"][label] <= 0.10
            for label in ("SUPPORTED", "REFUTED")
        ),
        "4_abstention_precision_ge_0.50": cand["abstention"]["precision"] >= 0.50,
        "5_failures_le_2": cand["failures"] <= 2,
        "6_p95_le_45s": cand["p95_latency_s"] <= 45,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise da linha v5.")
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--split", choices=("development", "test", "all"), required=True)
    parser.add_argument(
        "--conditions", nargs="*", default=[], help="ex.: v5_base_development_run1"
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    baseline_rows = load_rows(RESULTS / "dev" / "v3_all_run1.jsonl", args.split)
    baseline = summarize(baseline_rows)
    baseline["run_stability_vs_v4_records"] = run_stability(
        by_form(baseline_rows).get(ORIGINAL_FORM, []), v4_stored_v3()
    )
    report: dict = {"phase": args.phase, "split": args.split, "v3": baseline, "conditions": {}}
    base_original = by_form(baseline_rows)[ORIGINAL_FORM]
    for name in args.conditions:
        rows = load_rows(RESULTS / args.phase / f"{name}.jsonl", args.split)
        summary = summarize(rows)
        original = by_form(rows).get(ORIGINAL_FORM)
        if original and [r["parent_item_id"] for r in original] == [
            r["parent_item_id"] for r in base_original
        ]:
            expected = [r["expected_label"] for r in original]
            summary["bootstrap_vs_v3"] = paired_bootstrap(
                expected,
                [r["verdict"] for r in base_original],
                [r["verdict"] for r in original],
                [r["claim_family"] for r in original],
            )
            summary["gates"] = gates(summary, baseline, summary["bootstrap_vs_v3"])
        report["conditions"][name] = summary

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8", newline="\n")
    print_table(report)


def print_table(report: dict) -> None:
    print(
        "| Condição | Forma | n | Macro-F1 | 3 classes | Recall S/R/M/I | Abst. P/R | Falhas | P95 |"
    )
    print("|---|---|---|---|---|---|---|---|---|")
    entries = [("v3", report["v3"]), *report["conditions"].items()]
    for name, summary in entries:
        for form, m in sorted(summary["forms"].items()):
            recall = " / ".join(f"{m['recall'][k]:.2f}" for k in m["recall"])
            print(
                f"| {name} | {form} | {m['n']} | {m['macro_f1']:.3f} | {m['macro_f1_3class']:.3f} | "
                f"{recall} | {m['abstention']['precision']:.2f}/{m['abstention']['recall']:.2f} | "
                f"{m['failures']} | {m['p95_latency_s']:.1f} s |"
            )
    for name, summary in entries:
        extra = ""
        if "bootstrap_vs_v3" in summary:
            b = summary["bootstrap_vs_v3"]
            extra = f"; Δ vs v3 {b['delta']:+.3f} (IC {b['lower']:+.3f} a {b['upper']:+.3f})"
        consistency_value = summary["consistency"]
        consistency_text = f"{consistency_value:.3f}" if consistency_value is not None else "n/d"
        print(
            f"- {name}: consistência {consistency_text}; F1 agrupado {summary['pooled_macro_f1']:.3f}{extra}"
        )


if __name__ == "__main__":
    main()
