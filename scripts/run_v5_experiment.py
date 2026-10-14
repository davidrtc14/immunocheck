"""Executa uma condição da linha v5 (ou a v3 de referência) sobre itens v4 e paráfrases.

Fase `dev`: iteração permitida somente no split de calibração (development) para condições v5.
Fase `final`: execução única, exige `evaluation/refinement_v5/freeze.json` válido.
Os registros são checkpoints JSONL retomáveis; uma execução completa não é refeita.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from immunocheck.bootstrap import build_routed_text_pipeline, build_v5_text_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.paraphrase_set import ORIGINAL_FORM, PARAPHRASE_STYLES, load_paraphrases

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
PARAPHRASES = REPOSITORY / "evaluation/refinement_v5/paraphrases.jsonl"
RESULTS = REPOSITORY / "evaluation/refinement_v5/results"
FREEZE = REPOSITORY / "evaluation/refinement_v5/freeze.json"
FORMS = (ORIGINAL_FORM, *PARAPHRASE_STYLES)
CONDITIONS: dict[str, dict[str, bool] | None] = {
    "v3": None,
    "v5_base": {"multi_query": False, "reranker": False, "think": False},
    "v5_multiquery": {"multi_query": True, "reranker": False, "think": False},
    "v5_multiquery_reranker": {"multi_query": True, "reranker": True, "think": False},
    "v5_multiquery_think": {"multi_query": True, "reranker": False, "think": True},
}
FROZEN_FILES = (
    "src/immunocheck/application/structured_claim.py",
    "src/immunocheck/application/proposition_nli.py",
    "src/immunocheck/application/verdict_aggregation.py",
    "src/immunocheck/application/decomposed_pipeline.py",
    "src/immunocheck/retrieval/multi_query.py",
    "src/immunocheck/bootstrap.py",
    "src/immunocheck/infrastructure/ollama.py",
    "evaluation/refinement_v5/paraphrases.jsonl",
)


def file_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((REPOSITORY / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for name in FROZEN_FILES
    }


def verify_freeze() -> None:
    if not FREEZE.is_file():
        raise SystemExit("A fase final exige freeze.json registrado antes.")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))["sha256"]
    changed = [name for name, digest in file_hashes().items() if frozen.get(name) != digest]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))


def load_cases(split: str, forms: tuple[str, ...]) -> list[dict]:
    items = load_end_to_end_items(ITEMS, require_reviewed=True)
    by_id = {item.item_id: item for item in items}
    cases: list[dict] = []
    for item in items:
        if split != "all" and item.split.value != split:
            continue
        if ORIGINAL_FORM in forms:
            cases.append(
                {
                    "case_id": item.item_id,
                    "parent_item_id": item.item_id,
                    "form": ORIGINAL_FORM,
                    "claim": item.claim,
                }
            )
    for paraphrase in load_paraphrases(PARAPHRASES):
        parent = by_id[paraphrase.parent_item_id]
        if paraphrase.style in forms and (split == "all" or parent.split.value == split):
            cases.append(
                {
                    "case_id": paraphrase.paraphrase_id,
                    "parent_item_id": parent.item_id,
                    "form": paraphrase.style,
                    "claim": paraphrase.claim,
                }
            )
    for case in cases:
        parent = by_id[case["parent_item_id"]]
        case.update(
            claim_family=parent.claim_family,
            expected_label=parent.label.value,
            split=parent.split.value,
            evidence_chunk_ids=list(parent.evidence_chunk_ids),
        )
    return sorted(cases, key=lambda case: case["case_id"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimento v5 (ADR-049).")
    parser.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--split", choices=("development", "test", "all"), required=True)
    parser.add_argument("--forms", nargs="+", choices=FORMS, default=list(FORMS))
    parser.add_argument("--tag", default="run1", help="rótulo da repetição (ex.: run2)")
    args = parser.parse_args()

    options = CONDITIONS[args.condition]
    if args.phase == "dev" and options is not None and args.split != "development":
        parser.error("Na fase dev, condições v5 só rodam na calibração (development).")
    if args.phase == "final":
        verify_freeze()

    cases = load_cases(args.split, tuple(args.forms))
    output_dir = RESULTS / args.phase
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / f"{args.condition}_{args.split}_{args.tag}.jsonl"
    done: set[str] = set()
    if checkpoint.exists():
        done = {
            json.loads(line)["case_id"]
            for line in checkpoint.read_text("utf-8").splitlines()
            if line
        }
        if args.phase == "final" and len(done) >= len(cases):
            raise SystemExit("Esta condição final já foi executada; não se repete.")

    traces: list[dict] = []
    if options is None:
        pipeline = build_routed_text_pipeline()
    else:
        pipeline = build_v5_text_pipeline(**options, trace_sink=traces.append)
    with checkpoint.open("a", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            if case["case_id"] in done:
                continue
            traces.clear()
            started = time.perf_counter()
            failure = None
            try:
                result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=case["claim"]))
                verdict = result.verdict.value
                source_ids = [source.chunk_id for source in result.sources]
            except Exception as exc:  # noqa: BLE001 - falha técnica é dado do experimento
                verdict = Verdict.INSUFFICIENT_EVIDENCE.value
                source_ids, failure = [], type(exc).__name__
            trace = traces[-1] if traces else None
            if trace and trace.get("technical_abstention") and failure is None:
                failure = "TechnicalAbstention"
            record = {
                key: case[key]
                for key in (
                    "case_id",
                    "parent_item_id",
                    "form",
                    "split",
                    "claim_family",
                    "expected_label",
                    "evidence_chunk_ids",
                )
            }
            record.update(
                verdict=verdict,
                source_ids=source_ids,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                failure=failure,
                trace=trace,
            )
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(case["case_id"], "->", verdict, failure or "", flush=True)


if __name__ == "__main__":
    main()
