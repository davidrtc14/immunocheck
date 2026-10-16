"""Executa uma condição da Fase 18 (ADR-051) no conjunto v4 ou no teste externo.

Fase `dev`: só os itens `development` do v4, para verificar a ausência de regressão da V2.
Fase `final`: execução única, exige `evaluation/refinement_v6/freeze.json` válido. No teste
externo, o suplemento não versionado é conferido pelo sha256 registrado no congelamento dele.
Os registros são checkpoints JSONL retomáveis.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import time
from pathlib import Path

from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.bootstrap import build_routed_text_pipeline, build_v5_text_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict
from immunocheck.evaluation.end_to_end import load_end_to_end_items
from immunocheck.evaluation.paraphrase_set import ORIGINAL_FORM, PARAPHRASE_STYLES, load_paraphrases

REPOSITORY = Path(__file__).resolve().parents[1]
V4_ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
PARAPHRASES = REPOSITORY / "evaluation/refinement_v5/paraphrases.jsonl"
EXTERNAL = REPOSITORY / "evaluation/refinement_v6/external"
SUPPLEMENT = REPOSITORY / "output/external_v6/items_supplement.jsonl"
ROOT = REPOSITORY / "evaluation/refinement_v6"
RESULTS = ROOT / "results"
FREEZE = ROOT / "freeze.json"
FORMS = (ORIGINAL_FORM, *PARAPHRASE_STYLES)
QWEN36 = "qwen3.6:latest"
CONDITIONS = ("v3", "v5_multiquery", "v5_fixed", "v5_fixed_qwen36")
FROZEN_FILES = (
    "scripts/run_v6_experiment.py",
    "src/immunocheck/application/tolerant_verification.py",
    "src/immunocheck/application/structured_claim.py",
    "src/immunocheck/application/proposition_nli.py",
    "src/immunocheck/application/verdict_aggregation.py",
    "src/immunocheck/application/decomposed_pipeline.py",
    "src/immunocheck/retrieval/multi_query.py",
    "src/immunocheck/bootstrap.py",
    "src/immunocheck/infrastructure/ollama.py",
    "evaluation/refinement_v6/external/items.jsonl",
    "evaluation/refinement_v6/external/supplement_manifest.jsonl",
)


def file_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((REPOSITORY / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for name in FROZEN_FILES
    }


def verify_freeze() -> None:
    if not FREEZE.is_file():
        raise SystemExit(
            "A fase final exige evaluation/refinement_v6/freeze.json registrado antes."
        )
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))["sha256"]
    changed = [name for name, digest in file_hashes().items() if frozen.get(name) != digest]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))


def build_pipeline(condition: str, trace_sink):
    if condition == "v3":
        return build_routed_text_pipeline()
    model = QWEN36 if condition == "v5_fixed_qwen36" else None
    pipeline = build_v5_text_pipeline(
        model=model, multi_query=True, reranker=False, think=False, trace_sink=trace_sink
    )
    if condition == "v5_multiquery":
        return pipeline
    tolerant = TolerantPropositionJudge(pipeline.judge.client, pipeline.judge.max_output_tokens)
    return dataclasses.replace(pipeline, judge=tolerant)


def v4_cases(split: str, forms: tuple[str, ...]) -> list[dict]:
    items = load_end_to_end_items(V4_ITEMS, require_reviewed=True)
    by_id = {item.item_id: item for item in items}
    cases = [
        {
            "case_id": item.item_id,
            "parent_item_id": item.item_id,
            "form": ORIGINAL_FORM,
            "claim": item.claim,
        }
        for item in items
        if ORIGINAL_FORM in forms and (split == "all" or item.split.value == split)
    ]
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
        )
    return sorted(cases, key=lambda case: case["case_id"])


def external_cases() -> list[dict]:
    expected = json.loads((EXTERNAL / "freeze.json").read_text("utf-8"))
    if not SUPPLEMENT.is_file():
        raise SystemExit("Reconstrua o suplemento com scripts/build_external_testset.py.")
    digest = hashlib.sha256(SUPPLEMENT.read_text("utf-8").encode("utf-8")).hexdigest()
    if digest != expected["reconstructed_supplement_sha256"]:
        raise SystemExit("O suplemento reconstruído não confere com o sha256 congelado.")
    raw = [
        json.loads(line)
        for path in (EXTERNAL / "items.jsonl", SUPPLEMENT)
        for line in path.read_text("utf-8").splitlines()
        if line
    ]
    return sorted(
        (
            {
                "case_id": row["item_id"],
                "parent_item_id": row["item_id"],
                "form": ORIGINAL_FORM,
                "claim": row["claim"],
                "claim_family": row["claim_family"],
                "expected_label": row["label"],
                "split": "external",
                "corpus_topic_coverage": row.get("corpus_topic_coverage"),
                "external_flags": row.get("external_flags", []),
                "external_source": row.get("external_source"),
            }
            for row in raw
        ),
        key=lambda case: case["case_id"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimento v6 (ADR-051).")
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--dataset", choices=("v4", "external"), required=True)
    parser.add_argument("--phase", choices=("dev", "final"), required=True)
    parser.add_argument("--split", choices=("development", "test", "all"), default="all")
    parser.add_argument("--forms", nargs="+", choices=FORMS, default=list(FORMS))
    parser.add_argument("--limit", type=int, help="só os primeiros N casos (medição de latência)")
    parser.add_argument("--tag", default="run1")
    args = parser.parse_args()

    if args.phase == "dev" and (args.dataset != "v4" or args.split != "development"):
        parser.error("Na fase dev só os itens development do v4 podem ser usados.")
    if args.phase == "final":
        verify_freeze()
    cases = (
        external_cases() if args.dataset == "external" else v4_cases(args.split, tuple(args.forms))
    )
    if args.limit:
        cases = cases[: args.limit]

    output_dir = RESULTS / args.phase
    output_dir.mkdir(parents=True, exist_ok=True)
    name = f"{args.condition}_{args.dataset}_{args.split if args.dataset == 'v4' else 'all'}"
    checkpoint = output_dir / f"{name}_{args.tag}.jsonl"
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
    pipeline = build_pipeline(args.condition, traces.append)
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
            record = {key: value for key, value in case.items() if key != "claim"}
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
