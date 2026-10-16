"""Analisa o benchmark de extração (ADR-050): concordância, CER, latência, IC e gates."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
RESULTS = REPOSITORY / "evaluation/extraction_v1/results"
BOOTSTRAP_SAMPLES = 10_000
LATENCY_LIMIT_SECONDS = 45.0
LABELS = ("SUPPORTED", "REFUTED", "MISLEADING", "INSUFFICIENT_EVIDENCE")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def agreement_flags(rows: list[dict]) -> list[dict]:
    references = {
        row["parent_item_id"]: row["verdict"] for row in rows if row["modality"] == "reference"
    }
    flagged = []
    for row in rows:
        if row["modality"] == "reference":
            continue
        reference = references.get(row["parent_item_id"])
        agrees = (
            row["verdict"] is not None and reference is not None and row["verdict"] == reference
        )
        flagged.append({**row, "agrees": agrees})
    return flagged


def rate(rows: list[dict], key: str = "agrees") -> float | None:
    return sum(bool(row[key]) for row in rows) / len(rows) if rows else None


def p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, round(0.95 * len(ordered)) - 1)]


def macro_f1(rows: list[dict]) -> float:
    scores = []
    for label in LABELS:
        tp = sum(row["verdict"] == label and row["expected_label"] == label for row in rows)
        fp = sum(row["verdict"] == label and row["expected_label"] != label for row in rows)
        fn = sum(row["verdict"] != label and row["expected_label"] == label for row in rows)
        scores.append(2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.0)
    return sum(scores) / len(scores)


def paired_bootstrap(candidate: list[dict], baseline: list[dict], seed: int = 42) -> dict:
    """Diferença de concordância, reamostrando famílias de alegação (pareado por caso)."""

    base_by_case = {row["case_id"]: row for row in baseline}
    families: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
    for row in candidate:
        if row["case_id"] in base_by_case:
            families[row["claim_family"]].append(
                (row["agrees"], base_by_case[row["case_id"]]["agrees"])
            )
    names = sorted(families)
    if not names:
        return {"delta": None, "ci95": None, "families": 0}

    def delta(sample: list[str]) -> float:
        pairs = [pair for name in sample for pair in families[name]]
        return sum(a - b for a, b in pairs) / len(pairs)

    rng = random.Random(seed)
    draws = sorted(delta([rng.choice(names) for _ in names]) for _ in range(BOOTSTRAP_SAMPLES))
    return {
        "delta": round(delta(names), 4),
        "ci95": [
            round(draws[int(0.025 * len(draws))], 4),
            round(draws[int(0.975 * len(draws)) - 1], 4),
        ],
        "families": len(names),
    }


def summarize(rows: list[dict]) -> dict:
    flagged = agreement_flags(rows)
    by_template: dict[str, list[dict]] = defaultdict(list)
    by_modality: dict[str, list[dict]] = defaultdict(list)
    for row in flagged:
        by_template[f"{row['modality']}/{row['template']}"].append(row)
        by_modality[row["modality"]].append(row)
    images = by_modality.get("image", [])
    latencies: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        latencies[row["modality"]].append(row["latency_ms"] / 1000)
    return {
        "cases": len(flagged),
        "agreement": rate(flagged),
        "agreement_reserved": rate([row for row in flagged if row["template_split"] == "reserved"]),
        "agreement_by_modality": {name: rate(group) for name, group in sorted(by_modality.items())},
        "agreement_by_template": {name: rate(group) for name, group in sorted(by_template.items())},
        "image_cer_mean": statistics.mean(row["cer"] for row in images) if images else None,
        "image_markers_preserved": rate(images, "markers_preserved"),
        "image_rejections": sum(row["rejection"] is not None for row in images),
        "technical_failures": sum(row.get("failure") is not None for row in rows),
        "failure_rate": sum(row.get("failure") is not None for row in rows) / len(rows),
        "latency_p95_s": {name: p95(values) for name, values in sorted(latencies.items())},
        "macro_f1_vs_gold": {
            "reference_text": macro_f1([row for row in rows if row["modality"] == "reference"]),
            "multimodal_cases": macro_f1(flagged),
        },
    }


def gates(candidate: list[dict], baseline: list[dict]) -> dict:
    """Regra de decisão registrada em evaluation/extraction_v1/PROTOCOL.md (seção 6)."""

    cand, base = agreement_flags(candidate), agreement_flags(baseline)
    cand_summary, base_summary = summarize(candidate), summarize(baseline)
    overall = paired_bootstrap(cand, base)
    reserved = paired_bootstrap(
        [row for row in cand if row["template_split"] == "reserved"],
        [row for row in base if row["template_split"] == "reserved"],
    )
    clean = paired_bootstrap(
        [row for row in cand if row["template"] == "clean"],
        [row for row in base if row["template"] == "clean"],
    )
    results = {
        "G1_overall_gain": overall["delta"] is not None
        and overall["delta"] >= 0.10
        and overall["ci95"][0] > 0,
        "G2_reserved_gain": reserved["delta"] is not None
        and reserved["delta"] >= 0.05
        and reserved["ci95"][0] > 0,
        "G3_clean_non_regression": clean["delta"] is not None and clean["delta"] >= -0.05,
        "G4_image_cer_and_markers": cand_summary["image_cer_mean"] <= base_summary["image_cer_mean"]
        and cand_summary["image_markers_preserved"] >= base_summary["image_markers_preserved"],
        "G5_latency": all(
            value is not None and value <= LATENCY_LIMIT_SECONDS
            for value in cand_summary["latency_p95_s"].values()
        ),
        "G6_failures_and_rejections": cand_summary["failure_rate"] <= 0.02
        and cand_summary["image_rejections"] <= base_summary["image_rejections"],
    }
    return {
        "bootstrap": {"overall": overall, "reserved": reserved, "clean": clean},
        "gates": results,
        "passes": all(results.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise do benchmark de extração.")
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--conditions", nargs="+", default=["baseline", "improved"])
    parser.add_argument("--tag", default="run1")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = {
        name: load(RESULTS / args.phase / f"{name}_verdict_{args.tag}.jsonl")
        for name in args.conditions
    }
    report = {
        "phase": args.phase,
        "summaries": {name: summarize(rows) for name, rows in data.items()},
    }
    if "baseline" in data:
        report["decision"] = {
            name: gates(rows, data["baseline"]) for name, rows in data.items() if name != "baseline"
        }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
