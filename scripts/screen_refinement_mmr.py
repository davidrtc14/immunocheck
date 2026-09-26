"""Compara top 6 denso a top 20 denso selecionado por MMR, sem chamar LLM."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.domain.models import ExtractedClaim, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint
from immunocheck.retrieval.dense import (
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
    load_reusable_dense_vectors,
)
from immunocheck.retrieval.mmr import maximal_marginal_relevance
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
PHASE_A = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
PLAN = ROOT / "evaluation/refinement_v2/MMR_SELECTOR_SCREEN_PLAN.md"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
VECTORS = ROOT / "corpus/processed/dense_bge_m3.npz"
MANIFEST = ROOT / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = ROOT / "models"
OUTPUT = ROOT / "evaluation/results/refinement_v2/mmr_selector_screen.json"
MARKDOWN = ROOT / "evaluation/results/refinement_v2/MMR_SELECTOR_SCREEN.md"
CANDIDATE_DEPTH = 20
OUTPUT_DEPTH = 6
RELEVANCE_WEIGHT = 0.7


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise SystemExit("A triagem MMR já existe; o resultado registrado não será sobrescrito.")
    items = load_end_to_end_items(DATASET, require_reviewed=True)
    conclusive = tuple(item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE)
    records = load_refinement_checkpoint(PHASE_A)
    if len(records) != len(items):
        raise SystemExit("O checkpoint completo da fase A é obrigatório.")
    extracted_by_id = {
        str(record["item_id"]): str(record["extraction"]["claim"]) for record in records
    }
    evidence = load_evidence_jsonl(CORPUS)
    index, dense_manifest = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS,
        manifest_path=MANIFEST,
        corpus_path=CORPUS,
    )
    vectors_by_id, _ = load_reusable_dense_vectors(
        vectors_path=VECTORS,
        manifest_path=MANIFEST,
    )
    retriever = DenseRetriever(
        SentenceTransformerEmbedder(
            cache_folder=MODEL_CACHE,
            device="cpu",
            local_files_only=True,
        ),
        index,
        top_k=CANDIDATE_DEPTH,
    )
    rankings: dict[str, dict[str, list[str]]] = {"dense_top6": {}, "dense20_mmr6": {}}
    retrieval_latencies = []
    selection_latencies = []
    for item in conclusive:
        claim = ExtractedClaim(text=extracted_by_id[item.item_id], confidence=1.0)
        started = time.perf_counter()
        candidates = tuple(retriever.retrieve(claim))
        retrieval_latencies.append((time.perf_counter() - started) * 1000)
        started = time.perf_counter()
        selected = maximal_marginal_relevance(
            candidates,
            vectors_by_id,
            top_k=OUTPUT_DEPTH,
            relevance_weight=RELEVANCE_WEIGHT,
        )
        selection_latencies.append((time.perf_counter() - started) * 1000)
        rankings["dense_top6"][item.item_id] = [item.chunk_id for item in candidates[:6]]
        rankings["dense20_mmr6"][item.item_id] = [item.chunk_id for item in selected]

    systems = {
        name: _ranking_metrics(ranking, conclusive) for name, ranking in rankings.items()
    }
    baseline = systems["dense_top6"]
    candidate = systems["dense20_mmr6"]
    candidate["gained_item_ids"] = sorted(
        item_id
        for item_id, hit in candidate["hit_by_item"].items()
        if hit and not baseline["hit_by_item"][item_id]
    )
    candidate["lost_item_ids"] = sorted(
        item_id
        for item_id, hit in baseline["hit_by_item"].items()
        if hit and not candidate["hit_by_item"][item_id]
    )
    gates = {
        "global_hit_at_6": _gate(candidate["hits"], 24, "minimum"),
        "misleading_hit_at_6": _gate(
            candidate["per_class"][Verdict.MISLEADING.value]["hits"], 8, "minimum"
        ),
        "supported_no_hit_loss": _gate(
            candidate["per_class"][Verdict.SUPPORTED.value]["hits"]
            - baseline["per_class"][Verdict.SUPPORTED.value]["hits"],
            0,
            "minimum",
        ),
        "refuted_no_hit_loss": _gate(
            candidate["per_class"][Verdict.REFUTED.value]["hits"]
            - baseline["per_class"][Verdict.REFUTED.value]["hits"],
            0,
            "minimum",
        ),
        "selection_p95_ms": _gate(_latency(selection_latencies)["p95"], 100.0, "maximum"),
    }
    report = {
        "schema_version": 1,
        "experiment": "refinement_v2_mmr_selector_screen",
        "executed_at": datetime.now(UTC).isoformat(),
        "scope": "calibration_conclusive_only_no_llm",
        "dataset_sha256": _sha256(DATASET),
        "phase_a_checkpoint_sha256": _sha256(PHASE_A),
        "plan_sha256": _sha256(PLAN),
        "corpus_sha256": dense_manifest.corpus_sha256,
        "v1_test_items_loaded": 0,
        "holdout_v2_items_loaded": 0,
        "llm_calls": 0,
        "candidate_depth": CANDIDATE_DEPTH,
        "output_depth": OUTPUT_DEPTH,
        "relevance_weight": RELEVANCE_WEIGHT,
        "systems": systems,
        "latency_ms": {
            "dense_retrieval": _latency(retrieval_latencies),
            "mmr_selection": _latency(selection_latencies),
        },
        "gates": gates,
        "eligible_for_end_to_end": all(gate["passed"] for gate in gates.values()),
        "rankings": rankings,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(_render(report), encoding="utf-8", newline="\n")
    print(MARKDOWN.relative_to(ROOT))
    print(
        f"Hit@6: {baseline['hits']}/36 -> {candidate['hits']}/36; "
        f"gates: {sum(gate['passed'] for gate in gates.values())}/{len(gates)}"
    )
    return 0


def _ranking_metrics(rankings, items) -> dict[str, object]:
    hits = {}
    reciprocal_ranks = {}
    for item in items:
        relevant = set(item.evidence_chunk_ids)
        rank = next(
            (index for index, chunk_id in enumerate(rankings[item.item_id], start=1) if chunk_id in relevant),
            None,
        )
        hits[item.item_id] = rank is not None
        reciprocal_ranks[item.item_id] = 0.0 if rank is None else 1.0 / rank
    per_class = {}
    for label in (Verdict.SUPPORTED, Verdict.REFUTED, Verdict.MISLEADING):
        ids = [item.item_id for item in items if item.label is label]
        count = sum(hits[item_id] for item_id in ids)
        per_class[label.value] = {"hits": count, "items": len(ids), "rate": count / len(ids)}
    return {
        "hits": sum(hits.values()),
        "items": len(items),
        "hit_at_6": sum(hits.values()) / len(items),
        "mrr_at_6": statistics.fmean(reciprocal_ranks.values()),
        "per_class": per_class,
        "hit_by_item": hits,
    }


def _gate(value: float, threshold: float, direction: str) -> dict[str, object]:
    return {
        "value": value,
        "threshold": threshold,
        "direction": direction,
        "passed": value >= threshold if direction == "minimum" else value <= threshold,
    }


def _latency(values: list[float]) -> dict[str, float | int]:
    ordered = sorted(values)
    return {
        "median": statistics.median(ordered),
        "p95": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "samples": len(ordered),
    }


def _render(report: dict[str, object]) -> str:
    baseline = report["systems"]["dense_top6"]
    candidate = report["systems"]["dense20_mmr6"]
    lines = [
        "# Triagem do seletor MMR — calibração v2",
        "",
        "A triagem usa somente 36 itens conclusivos da calibração, sem chamadas de LLM,",
        "teste v1 ou holdout v2.",
        "",
        "| Sistema | Hit@6 | MRR@6 | SUPPORTED | REFUTED | MISLEADING |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, system in (("Denso top 6", baseline), ("Denso 20 → MMR 6", candidate)):
        per_class = system["per_class"]
        lines.append(
            f"| {name} | {system['hits']}/36 ({system['hit_at_6']:.1%}) | "
            f"{system['mrr_at_6']:.3f} | "
            f"{per_class['SUPPORTED']['hits']}/12 | "
            f"{per_class['REFUTED']['hits']}/12 | "
            f"{per_class['MISLEADING']['hits']}/12 |"
        )
    lines.extend(["", "## Gates", "", "| Gate | Valor | Limite | Estado |", "|---|---:|---:|---|"])
    for name, gate in report["gates"].items():
        operator = "≥" if gate["direction"] == "minimum" else "≤"
        state = "Passou" if gate["passed"] else "Falhou"
        lines.append(f"| `{name}` | {gate['value']} | {operator} {gate['threshold']} | {state} |")
    state = "elegível" if report["eligible_for_end_to_end"] else "não elegível"
    lines.extend(
        [
            "",
            f"**Decisão:** seletor MMR {state} para avaliação fim a fim.",
            "",
            "MMR mede diversidade no espaço BGE-M3; não demonstra suficiência factual nem",
            "substitui a avaliação fim a fim.",
        ]
    )
    return "\n".join(lines) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
