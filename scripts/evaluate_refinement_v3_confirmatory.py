"""Executa uma única confirmação da candidata v3 congelada em 32 itens novos."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from evaluate_refinement_calibration import (
    AlwaysSupportedVerifier,
    _append,
    _run_condition,
    _serialize,
)

from immunocheck.application.text_components import (
    GuardedFaithfulnessVerifier,
    LLMCitationSelector,
    LLMClaimExtractor,
    LLMClaimRouteAnalyzer,
    LLMFaithfulnessVerifier,
    LLMRelationVerdictGenerator,
    LLMVerdictGenerator,
    ModelOutputError,
)
from immunocheck.domain.models import (
    DraftVerdict,
    FactCheckResult,
    Verdict,
)
from immunocheck.evaluation.confirmatory import (
    CONFIRMATORY_CONDITIONS,
    summarize_confirmatory_records,
    validate_confirmatory_checkpoint,
    validate_confirmatory_dataset,
)
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_calibration import load_family_ids
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint
from immunocheck.infrastructure.ollama import OllamaError, OllamaStructuredClient
from immunocheck.retrieval.dense import (
    DenseIndexError,
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.document_expansion import expand_document_candidates
from immunocheck.retrieval.pilot_corpus import CorpusLoadError, load_evidence_jsonl

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v3/confirmatory/items.jsonl"
MANIFEST = ROOT / "evaluation/refinement_v3/confirmatory/manifest.json"
PROTOCOL = ROOT / "evaluation/refinement_v3/confirmatory/PROTOCOL.md"
CALIBRATION = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
FROZEN_TEST_FAMILIES = ROOT / "evaluation/refinement_v2/FROZEN_TEST_FAMILIES.txt"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
VECTORS = ROOT / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST = ROOT / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = ROOT / "models"
DEFAULT_CHECKPOINT = ROOT / "evaluation/results/refinement_v3/confirmatory.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation/results/refinement_v3/confirmatory.json"
BASELINE, CANDIDATE = CONFIRMATORY_CONDITIONS
TOP_K = 15
DIRECT_TOP_K = 6

FROZEN_HASHES = {
    ROOT / "src/immunocheck/application/text_components.py": (
        "053378ab07450192e9684f886e7c1a0c153789bb7f632197c4283150281915e4"
    ),
    ROOT / "src/immunocheck/retrieval/document_expansion.py": (
        "b00be06050c1b15811265bdbeeea06faf66c6f6e7c23e1b1d691590eacd4a1b3"
    ),
    CORPUS: "401bed2cad62142b30e2879b6f91e6f05098ab9ac86191316ba65685af36b19a",
    DENSE_MANIFEST: "2abbf3075a8d2e80258c20cad581b2a00d5ae3f8c5cdfcaa790447c1a4f6605c",
    VECTORS: "8f6c5520a79b72cdd738534d472751fef3f1138b38a479d895f5ac32d7d0ddbd",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:8b"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O resultado confirmatório já existe e não pode ser sobrescrito.")

    manifest = _validate_preflight()
    evidence = load_evidence_jsonl(CORPUS)
    items = load_end_to_end_items(
        DATASET,
        valid_chunk_ids={chunk.chunk_id for chunk in evidence},
        require_reviewed=False,
    )
    calibration = load_end_to_end_items(CALIBRATION, require_reviewed=True)
    excluded = set(
        load_family_ids(FROZEN_TEST_FAMILIES.read_text("utf-8").splitlines())
    )
    excluded.update(item.claim_family for item in calibration if item.claim_family)
    validate_confirmatory_dataset(items, excluded_families=excluded)

    checkpoint = load_refinement_checkpoint(args.checkpoint)
    validate_confirmatory_checkpoint(checkpoint, items)
    if len(checkpoint) < len(items):
        components = _build_components(args.model, evidence)
        for index, item in enumerate(items[len(checkpoint) :], start=len(checkpoint) + 1):
            record = _evaluate_item(item, components, evidence)
            _append(args.checkpoint, record)
            candidate = record["conditions"][CANDIDATE]
            print(
                f"[{index}/{len(items)}] {item.item_id}: "
                f"{record['routing']['route']} -> {candidate['verdict']}",
                flush=True,
            )

    records = load_refinement_checkpoint(args.checkpoint)
    summary = summarize_confirmatory_records(records, items)
    report = {
        "schema_version": 1,
        "experiment": "refinement_v3_confirmatory_once",
        "executed_at": datetime.now(UTC).isoformat(),
        "preexecution_manifest_sha256": _sha256(MANIFEST),
        "dataset_sha256": manifest["dataset_sha256"],
        "protocol_sha256": manifest["protocol_sha256"],
        "candidate_source_commit": manifest["candidate_source_commit"],
        "partition": "new_confirmatory_test_families",
        "v1_final_test_items_loaded": 0,
        "model": args.model,
        "temperature": 0,
        "seed": 42,
        "retrieval": "bge_m3_dense_top_15",
        "conditions": list(CONFIRMATORY_CONDITIONS),
        "curation": manifest["curation"],
        "external_human_review_claimed": False,
        "checkpoint_sha256": _sha256(args.checkpoint),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(ROOT)}")
    return 0


def _validate_preflight() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    if manifest["status"] != "confirmatory_ready_frozen_unexecuted":
        raise RuntimeError("O manifesto não autoriza a execução confirmatória.")
    if _sha256(DATASET) != manifest["dataset_sha256"]:
        raise RuntimeError("O conjunto confirmatório diverge do hash congelado.")
    if _sha256(PROTOCOL) != manifest["protocol_sha256"]:
        raise RuntimeError("O protocolo confirmatório diverge do hash congelado.")
    for path, expected in FROZEN_HASHES.items():
        if _normalized_sha256(path) != expected:
            raise RuntimeError(f"Componente congelado divergente: {path.relative_to(ROOT)}")
    return manifest


def _build_components(model: str, evidence) -> dict[str, object]:
    dense_index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS,
        manifest_path=DENSE_MANIFEST,
        corpus_path=CORPUS,
    )
    client = OllamaStructuredClient(model=model)
    return {
        "extractor": LLMClaimExtractor(client),
        "retriever": DenseRetriever(
            SentenceTransformerEmbedder(
                cache_folder=MODEL_CACHE,
                device="cpu",
                local_files_only=True,
            ),
            dense_index,
            top_k=TOP_K,
        ),
        "baseline_generator": LLMVerdictGenerator(client),
        "baseline_verifier": GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)),
        "direct_generator": LLMVerdictGenerator(client),
        "relation_generator": LLMRelationVerdictGenerator(client),
        "router": LLMClaimRouteAnalyzer(client),
        "selector": LLMCitationSelector(client),
    }


def _evaluate_item(item, components: dict[str, object], corpus) -> dict[str, object]:
    shared_started = time.perf_counter()
    shared_error = None
    extracted = None
    evidence = ()
    try:
        extracted = components["extractor"].extract(item.claim)  # type: ignore[attr-defined]
        if extracted is not None:
            evidence = tuple(components["retriever"].retrieve(extracted))  # type: ignore[attr-defined]
    except (CorpusLoadError, DenseIndexError, ModelOutputError, OllamaError, ValueError) as exc:
        shared_error = f"{type(exc).__name__}: {exc}"
    shared_latency = (time.perf_counter() - shared_started) * 1000
    extraction = {
        "claim": extracted.text if extracted else None,
        "confidence": extracted.confidence if extracted else None,
        "multiple_claims_detected": extracted.multiple_claims_detected if extracted else None,
        "retrieved_source_ids": [chunk.chunk_id for chunk in evidence],
        "latency_ms": shared_latency,
        "technical_error": shared_error,
    }
    if extracted is None or shared_error:
        fallback = FactCheckResult.insufficient(
            "Não foi possível preparar a alegação para avaliação local."
        )
        conditions = {
            name: _serialize(fallback, shared_latency, technical_error=shared_error)
            for name in CONFIRMATORY_CONDITIONS
        }
        routing = {
            "route": "PREPARATION_FAILURE",
            "explanation": "Falha antes do roteamento.",
            "latency_ms": 0.0,
            "technical_error": shared_error,
        }
        citation = {"called": False, "latency_ms": 0.0, "technical_error": None}
    else:
        baseline_result, baseline_latency, baseline_error = _run_condition(
            item.claim,
            extracted,
            evidence[:DIRECT_TOP_K],
            components["baseline_generator"],
            components["baseline_verifier"],
        )
        baseline = _serialize(
            baseline_result,
            shared_latency + baseline_latency,
            technical_error=baseline_error,
        )
        candidate, routing, citation = _run_candidate(
            item.claim,
            extracted,
            evidence,
            corpus,
            components,
            shared_latency,
        )
        conditions = {BASELINE: baseline, CANDIDATE: candidate}
    return {
        "item_id": item.item_id,
        "claim_family": item.claim_family,
        "expected_label": item.label.value,
        "extraction": extraction,
        "routing": routing,
        "hierarchical_citation": citation,
        "conditions": conditions,
    }


def _run_candidate(input_text, claim, evidence, corpus, components, shared_latency):
    route_started = time.perf_counter()
    route_error = None
    try:
        assessment = components["router"].analyze(claim)
        route = assessment.route
        route_explanation = assessment.explanation
    except (ModelOutputError, OllamaError, ValueError) as exc:
        route_error = f"{type(exc).__name__}: {exc}"
        route = "ROUTING_FAILURE"
        route_explanation = "Não foi possível determinar com segurança a forma da alegação."
    route_latency = (time.perf_counter() - route_started) * 1000

    inference_latency = 0.0
    decision_error = route_error
    if route == "GENERAL_SIMPLE":
        result, inference_latency, decision_error = _run_condition(
            input_text,
            claim,
            evidence[:DIRECT_TOP_K],
            components["direct_generator"],
            AlwaysSupportedVerifier(),
        )
    elif route == "PREMISE_CONCLUSION":
        result, inference_latency, decision_error = _run_condition(
            input_text,
            claim,
            evidence,
            components["relation_generator"],
            AlwaysSupportedVerifier(),
        )
    else:
        result = FactCheckResult.insufficient(
            route_explanation,
            claim=claim.text,
            multiple_claims_detected=claim.multiple_claims_detected,
        )

    candidate = _serialize(
        result,
        shared_latency + route_latency + inference_latency,
        technical_error=decision_error,
    )
    selection_latency = 0.0
    selection_error = None
    candidate_count = 0
    if result.verdict is not Verdict.INSUFFICIENT_EVIDENCE and decision_error is None:
        draft = DraftVerdict(
            verdict=result.verdict,
            explanation=result.explanation,
            source_ids=tuple(candidate["source_ids"]),
            correct_fact=result.correct_fact,
            omitted_or_distorted=result.omitted_or_distorted,
        )
        selection_started = time.perf_counter()
        try:
            seeds = components["selector"].select(claim, draft, evidence)
            expanded = expand_document_candidates(
                corpus,
                seeds,
                first_chunks=4,
                neighbor_radius=1,
                max_candidates=20,
            )
            candidate_count = len(expanded)
            selected_draft = DraftVerdict(
                verdict=draft.verdict,
                explanation=draft.explanation,
                source_ids=tuple(seeds),
                correct_fact=draft.correct_fact,
                omitted_or_distorted=draft.omitted_or_distorted,
            )
            candidate["source_ids"] = list(
                components["selector"].select(claim, selected_draft, expanded)
            )
        except (ModelOutputError, OllamaError, ValueError) as exc:
            selection_error = f"{type(exc).__name__}: {exc}"
        selection_latency = (time.perf_counter() - selection_started) * 1000
        candidate["latency_ms"] = float(candidate["latency_ms"]) + selection_latency
        candidate["technical_error"] = selection_error
    routing = {
        "route": route,
        "explanation": route_explanation,
        "latency_ms": route_latency,
        "technical_error": route_error,
    }
    citation = {
        "called": result.verdict is not Verdict.INSUFFICIENT_EVIDENCE,
        "candidate_count": candidate_count,
        "latency_ms": selection_latency,
        "technical_error": selection_error,
    }
    return candidate, routing, citation


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
