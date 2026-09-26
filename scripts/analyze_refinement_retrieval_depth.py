"""Mede Hit@k denso da calibração v2 sem chamar LLM ou abrir holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from immunocheck.domain.models import ExtractedClaim, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.refinement_diagnostics import (
    RETRIEVAL_DEPTHS,
    render_refinement_retrieval_depth,
    summarize_refinement_retrieval_depth,
)
from immunocheck.evaluation.refinement_experiment import load_refinement_checkpoint
from immunocheck.retrieval.dense import (
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.pilot_corpus import PilotCorpusBM25Retriever, load_evidence_jsonl
from immunocheck.retrieval.rrf import reciprocal_rank_fusion

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/refinement_v2/calibration/adjudicated_items.jsonl"
RECORDS = ROOT / "evaluation/results/refinement_v2/calibration_phase_a.jsonl"
CORPUS = ROOT / "corpus/processed/chunks.jsonl"
VECTORS = ROOT / "corpus/processed/dense_bge_m3.npz"
MANIFEST = ROOT / "corpus/processed/dense_bge_m3.json"
MODEL_CACHE = ROOT / "models"
OUTPUT_DIR = ROOT / "evaluation/results/refinement_v2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    json_output = OUTPUT_DIR / "calibration_retrieval_depth.json"
    markdown_output = OUTPUT_DIR / "CALIBRATION_RETRIEVAL_DEPTH.md"
    if not args.overwrite and (json_output.exists() or markdown_output.exists()):
        parser.error("O diagnóstico já existe; use --overwrite apenas para reprodução.")

    items = load_end_to_end_items(DATASET, require_reviewed=True)
    conclusive = tuple(item for item in items if item.label is not Verdict.INSUFFICIENT_EVIDENCE)
    records = load_refinement_checkpoint(RECORDS)
    extracted_by_id = {
        str(record["item_id"]): str(record["extraction"]["claim"]) for record in records
    }
    evidence = load_evidence_jsonl(CORPUS)
    index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS,
        manifest_path=MANIFEST,
        corpus_path=CORPUS,
    )
    retriever = DenseRetriever(
        SentenceTransformerEmbedder(
            cache_folder=MODEL_CACHE,
            device="cpu",
            local_files_only=True,
        ),
        index,
        top_k=RETRIEVAL_DEPTHS[-1],
    )
    bm25 = PilotCorpusBM25Retriever(evidence, top_k=RETRIEVAL_DEPTHS[-1])
    rankings = {
        "original_claim_dense": {},
        "phase_a_extracted_claim_dense": {},
        "phase_a_extracted_claim_bm25": {},
        "phase_a_extracted_claim_hybrid_rrf": {},
    }
    for item in conclusive:
        queries = {
            "original_claim_dense": item.claim,
            "phase_a_extracted_claim_dense": extracted_by_id[item.item_id],
        }
        for name, text in queries.items():
            result = retriever.retrieve(ExtractedClaim(text=text, confidence=1.0))
            rankings[name][item.item_id] = [evidence.chunk_id for evidence in result]
        extracted = ExtractedClaim(text=extracted_by_id[item.item_id], confidence=1.0)
        lexical = tuple(bm25.retrieve(extracted))
        semantic_ids = rankings["phase_a_extracted_claim_dense"][item.item_id]
        evidence_by_id = {item.chunk_id: item for item in evidence}
        semantic = tuple(evidence_by_id[chunk_id] for chunk_id in semantic_ids)
        hybrid = reciprocal_rank_fusion(
            (lexical, semantic),
            top_k=RETRIEVAL_DEPTHS[-1],
            rank_constant=60,
        )
        rankings["phase_a_extracted_claim_bm25"][item.item_id] = [item.chunk_id for item in lexical]
        rankings["phase_a_extracted_claim_hybrid_rrf"][item.item_id] = [
            item.chunk_id for item in hybrid
        ]

    report = summarize_refinement_retrieval_depth(rankings, items)
    report["inputs"] = {
        "dataset": str(DATASET.relative_to(ROOT)).replace("\\", "/"),
        "dataset_sha256": _sha256(DATASET),
        "phase_a_records": str(RECORDS.relative_to(ROOT)).replace("\\", "/"),
        "phase_a_records_sha256": _sha256(RECORDS),
        "corpus_sha256": _sha256(CORPUS),
        "dense_vectors_sha256": _sha256(VECTORS),
        "dense_manifest_sha256": _sha256(MANIFEST),
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_output.write_text(
        render_refinement_retrieval_depth(report), encoding="utf-8", newline="\n"
    )
    print(json_output.relative_to(ROOT))
    print(markdown_output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
