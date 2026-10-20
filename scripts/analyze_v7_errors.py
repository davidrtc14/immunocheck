"""Análise de erros da v7 (cascata C6) na execução única da Fase 20, sem reexecutar o veredito.

Lê os registros de `output/v7_runs/final/` (C6 e v3, no teste do C7 e no teste externo 2) e
recalcula, só na CPU, a busca densa (BGE-M3, top 15, corpus v1) sobre o texto bruto de cada alegação.
A busca da pipeline usa a alegação extraída pelo modelo, quase sempre igual ao texto; por isso o
resultado é uma aproximação, declarada como tal. Com ela, cada erro do C7 é separado em erro com o
documento de origem recuperado (julgamento) ou sem ele (busca).

Saídas:
- `evaluation/refinement_v7/error_analysis.json`: só agregados, sem texto de alegação nem trechos.
- `output/error_analysis/`: registros por item e a amostra para codificação manual (fora do Git).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_v7_experiment import c7_cases, external2_cases  # type: ignore[import-not-found]

from immunocheck.bootstrap import (
    DEFAULT_CORPUS_PATH,
    DEFAULT_DENSE_MANIFEST_PATH,
    DEFAULT_DENSE_VECTORS_PATH,
    DEFAULT_MODEL_CACHE,
)
from immunocheck.retrieval.dense import SentenceTransformerEmbedder, load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

REPOSITORY = Path(__file__).resolve().parents[1]
FINAL = REPOSITORY / "output/v7_runs/final"
LOCAL = REPOSITORY / "output/error_analysis"
REPORT = REPOSITORY / "evaluation/refinement_v7/error_analysis.json"
TOP_K = 15
SAMPLE_SIZE = 60
SUPPORTED, REFUTED, MISLEADING, INSUFFICIENT = (
    "SUPPORTED",
    "REFUTED",
    "MISLEADING",
    "INSUFFICIENT_EVIDENCE",
)
NOT_SUPPORTED = {REFUTED, MISLEADING}


def load(name: str) -> dict[str, dict]:
    path = FINAL / name
    rows = [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]
    return {row["case_id"]: row for row in rows}


def document_of(chunk_id: str) -> str:
    return chunk_id.split(":", 1)[0]


def error_type(expected: str, predicted: str) -> str:
    """Tipos de erro do C7, do mais ao menos danoso."""

    if expected == predicted:
        return "correct"
    if predicted == SUPPORTED and expected in NOT_SUPPORTED:
        return "grave"
    if expected == SUPPORTED:
        return "true_claim_dropped"
    if {expected, predicted} == NOT_SUPPORTED:
        return "degree_refuted_misleading"
    if predicted == INSUFFICIENT:
        return "undue_abstention"
    return "overconfident_on_insufficient"


def retrieve_all(claims: dict[str, str]) -> dict[str, list]:
    evidence = load_evidence_jsonl(DEFAULT_CORPUS_PATH)
    index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=DEFAULT_DENSE_VECTORS_PATH,
        manifest_path=DEFAULT_DENSE_MANIFEST_PATH,
        corpus_path=DEFAULT_CORPUS_PATH,
    )
    embedder = SentenceTransformerEmbedder(
        cache_folder=DEFAULT_MODEL_CACHE, device="cpu", local_files_only=True
    )
    ids = list(claims)
    vectors = embedder.encode(tuple(claims[case_id] for case_id in ids))
    return {
        case_id: [
            (item.chunk_id, round(float(item.retrieval_score), 4), item.document_title)
            for item in index.search(vector, top_k=TOP_K)
        ]
        for case_id, vector in zip(ids, vectors, strict=True)
    }


def c7_analysis(retrieved: dict[str, list]) -> tuple[dict, list[dict]]:
    cases = {case["case_id"]: case for case in c7_cases("test")}
    c6, v3 = load("C6_c7_final.jsonl"), load("v3_c7_final.jsonl")
    items = []
    for case_id, case in cases.items():
        row, top = c6[case_id], retrieved[case_id]
        trace = row.get("trace") or {}
        items.append(
            {
                "case_id": case_id,
                "expected": case["expected_label"],
                "predicted": row["verdict"],
                "v3": v3[case_id]["verdict"],
                "misleading_subtype": case["misleading_subtype"],
                "chunk_hit": case["source_chunk_id"] in {chunk for chunk, _, _ in top},
                "document_hit": document_of(case["source_chunk_id"])
                in {document_of(chunk) for chunk, _, _ in top},
                "primary": trace.get("primary_verdict"),
                "verified": bool(trace.get("verified")),
                "switched": bool(trace.get("verified"))
                and trace.get("final_verdict") != trace.get("primary_verdict"),
                "failure": row["failure"],
            }
        )
    for item in items:
        item["error_type"] = error_type(item["expected"], item["predicted"])

    types = Counter(item["error_type"] for item in items)
    by_type_hit: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        by_type_hit[item["error_type"]]["document_hit" if item["document_hit"] else "miss"] += 1
    errors = [item for item in items if item["error_type"] != "correct"]
    subtypes: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        if item["expected"] == MISLEADING:
            subtypes[item["misleading_subtype"] or "none"][item["predicted"]] += 1
    cascade = Counter(
        f"{item['expected']}: {item['primary']} -> {item['predicted']}"
        for item in items
        if item["switched"]
    )
    dropped = Counter(
        "cascade" if item["switched"] else "primary"
        for item in items
        if item["error_type"] == "true_claim_dropped"
    )
    confusion: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        confusion[item["expected"]][item["predicted"]] += 1
    report = {
        "n": len(items),
        "retrieval_proxy": {
            "chunk_hit_rate": round(sum(i["chunk_hit"] for i in items) / len(items), 3),
            "document_hit_rate": round(sum(i["document_hit"] for i in items) / len(items), 3),
            "errors_with_document_retrieved": sum(i["document_hit"] for i in errors),
            "errors_total": len(errors),
        },
        "error_types": dict(types.most_common()),
        "error_types_by_retrieval": {k: dict(v) for k, v in sorted(by_type_hit.items())},
        "confusion_c6": {k: dict(v) for k, v in sorted(confusion.items())},
        "misleading_by_subtype": {k: dict(v) for k, v in sorted(subtypes.items())},
        "cascade_switches": dict(sorted(cascade.items())),
        "true_claims_dropped_by_stage": dict(dropped),
        "technical_failures": sum(1 for i in items if i["failure"]),
    }
    return report, items


def external_analysis(retrieved: dict[str, list]) -> tuple[dict, list[dict]]:
    cases = {case["case_id"]: case for case in external2_cases()}
    c6, v3 = load("C6_external2_final.jsonl"), load("v3_external2_final.jsonl")
    items = []
    for case_id, case in cases.items():
        row, top = c6[case_id], retrieved[case_id]
        trace = row.get("trace") or {}
        items.append(
            {
                "case_id": case_id,
                "expected": case["expected_label"],
                "predicted": row["verdict"],
                "v3": v3[case_id]["verdict"],
                "topic": case["corpus_topic_coverage"] or "unknown",
                "top1_score": top[0][1],
                "switched_to_insufficient": bool(trace.get("verified"))
                and trace.get("final_verdict") == INSUFFICIENT,
                "failure": row["failure"],
            }
        )

    def reason(item: dict) -> str:
        if item["failure"]:
            return "technical_failure"
        if item["switched_to_insufficient"]:
            return "cascade_verification"
        return "primary_abstention"

    abstained = [item for item in items if item["predicted"] == INSUFFICIENT]
    concluded = [item for item in items if item["predicted"] != INSUFFICIENT]
    scores = sorted(item["top1_score"] for item in items)
    terciles = (scores[len(scores) // 3], scores[2 * len(scores) // 3])

    def band(score: float) -> str:
        return "low" if score < terciles[0] else "mid" if score < terciles[1] else "high"

    by_band: dict[str, Counter] = defaultdict(Counter)
    by_topic: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        state = "abstained" if item["predicted"] == INSUFFICIENT else "concluded"
        by_band[band(item["top1_score"])][state] += 1
        by_topic[item["topic"]][state] += 1
    report = {
        "n": len(items),
        "abstained": len(abstained),
        "abstention_reasons": dict(Counter(reason(item) for item in abstained).most_common()),
        "similarity_terciles": [round(value, 4) for value in terciles],
        "by_top1_similarity_band": {k: dict(by_band[k]) for k in ("low", "mid", "high")},
        "by_topic": {k: dict(v) for k, v in sorted(by_topic.items())},
        "mean_top1_score": {
            "abstained": round(sum(i["top1_score"] for i in abstained) / len(abstained), 4),
            "concluded": round(sum(i["top1_score"] for i in concluded) / len(concluded), 4),
        },
    }
    return report, items


def write_sample(items: list[dict], retrieved: dict[str, list], claims: dict[str, str]) -> None:
    """Amostra aleatória das abstenções para codificação manual (local, contém texto)."""

    abstained = sorted(
        (item for item in items if item["predicted"] == INSUFFICIENT and not item["failure"]),
        key=lambda item: item["case_id"],
    )
    sample = random.Random(42).sample(abstained, min(SAMPLE_SIZE, len(abstained)))
    with (LOCAL / "abstention_sample.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in sorted(sample, key=lambda item: item["case_id"]):
            handle.write(
                json.dumps(
                    {
                        "case_id": item["case_id"],
                        "claim": claims[item["case_id"]],
                        "expected": item["expected"],
                        "topic": item["topic"],
                        "top3": [
                            {"title": title, "score": score}
                            for _, score, title in retrieved[item["case_id"]][:3]
                        ],
                        "code": None,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise de erros da v7 (Fase 20).")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()

    claims = {case["case_id"]: case["claim"] for case in c7_cases("test")}
    claims.update({case["case_id"]: case["claim"] for case in external2_cases()})
    retrieved = retrieve_all(claims)
    c7_report, c7_items = c7_analysis(retrieved)
    ext_report, ext_items = external_analysis(retrieved)

    LOCAL.mkdir(parents=True, exist_ok=True)
    for name, rows in (("c7_items.jsonl", c7_items), ("external2_items.jsonl", ext_items)):
        (LOCAL / name).write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
        )
    write_sample(ext_items, retrieved, claims)

    report = {
        "scope": "descritiva, sobre a execução única da Fase 20; nenhuma condição foi reexecutada",
        "retrieval_proxy": "BGE-M3 denso, top 15, corpus v1, sobre o texto bruto da alegação",
        "c7": c7_report,
        "external2": ext_report,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
