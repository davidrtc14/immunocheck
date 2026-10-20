"""Executa uma condição da Fase 20 (ADR-054 e ADR-055) no C7 ou no teste externo 2.

Fase `dev`: só o split de desenvolvimento do C7, livre para iterar (Adendo 1 do protocolo).
Fase `final`: execução única no teste do C7 e no teste externo 2, com as condições do Adendo 3 (v3,
`v5_fixed` e C6). Exige `evaluation/refinement_v7/verdict_freeze.json`, gravado antes com
`--write-freeze`, e confere os hashes do código, do C7 e dos itens locais do teste externo 2.
Os registros são checkpoints JSONL retomáveis, fora do Git em `output/v7_runs/`: os traces contêm
trechos do corpus e, no teste externo 2, texto derivado das alegações das agências.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_v6_experiment import build_pipeline as build_v6_pipeline  # type: ignore[import-not-found]

from immunocheck.bootstrap_v7 import CANDIDATES, build_cascade_pipeline, build_v7_text_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict

REPOSITORY = Path(__file__).resolve().parents[1]
C7_ITEMS = REPOSITORY / "evaluation/refinement_v7/items.jsonl"
C7_FREEZE = REPOSITORY / "evaluation/refinement_v7/freeze.json"
EXTERNAL2 = REPOSITORY / "evaluation/refinement_v7/external2"
EXTERNAL2_ITEMS = REPOSITORY / "output/external2_v7/items.jsonl"
VERDICT_FREEZE = REPOSITORY / "evaluation/refinement_v7/verdict_freeze.json"
RUNS = REPOSITORY / "output/v7_runs"
BASELINES = ("v3", "v5_fixed")
FINAL_CONDITIONS = ("v3", "v5_fixed", "C6")
DATASETS = ("c7", "external2")
FROZEN_FILES = (
    "scripts/run_v7_experiment.py",
    "scripts/run_v6_experiment.py",
    "scripts/analyze_v7_final.py",
    "scripts/analyze_v6.py",
    "src/immunocheck/bootstrap.py",
    "src/immunocheck/bootstrap_v7.py",
    "src/immunocheck/application/cascade.py",
    "src/immunocheck/application/routed_pipeline.py",
    "src/immunocheck/application/text_components.py",
    "src/immunocheck/application/decomposed_pipeline.py",
    "src/immunocheck/application/tolerant_verification.py",
    "src/immunocheck/application/structured_claim.py",
    "src/immunocheck/application/proposition_nli.py",
    "src/immunocheck/application/verdict_aggregation.py",
    "src/immunocheck/retrieval/multi_query.py",
    "src/immunocheck/retrieval/document_expansion.py",
    "src/immunocheck/infrastructure/ollama.py",
    "src/immunocheck/infrastructure/context_budget.py",
    "src/immunocheck/evaluation/verdict_v7.py",
    "evaluation/refinement_v7/items.jsonl",
    "evaluation/refinement_v7/freeze.json",
    "evaluation/refinement_v7/PROTOCOL.md",
    "evaluation/refinement_v7/external2/manifest.jsonl",
    "evaluation/refinement_v7/external2/freeze.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def file_hashes() -> dict[str, str]:
    return {name: _sha256(REPOSITORY / name) for name in FROZEN_FILES}


def check_datasets() -> None:
    """O teste do C7 e os itens locais do teste externo 2 precisam bater com os congelamentos."""

    frozen = json.loads(C7_FREEZE.read_text("utf-8"))
    rows = [json.loads(line) for line in C7_ITEMS.read_text("utf-8").splitlines() if line]
    test = [row for row in rows if row["split"] == "test"]
    digest = hashlib.sha256(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in test).encode()
    ).hexdigest()
    if len(test) != frozen["test_items"] or digest != frozen["test_items_sha256"]:
        raise SystemExit("O teste do C7 não confere com evaluation/refinement_v7/freeze.json.")
    external = json.loads((EXTERNAL2 / "freeze.json").read_text("utf-8"))
    if not EXTERNAL2_ITEMS.is_file():
        raise SystemExit("Reconstrua o teste externo 2 com scripts/build_external2_testset.py.")
    local = hashlib.sha256(EXTERNAL2_ITEMS.read_text("utf-8").encode("utf-8")).hexdigest()
    if local != external["local_items_sha256"]:
        raise SystemExit("Os itens locais do teste externo 2 não conferem com o congelamento.")


def write_freeze() -> None:
    """Registra os hashes do código e dos conjuntos, e o modelo local, antes da fase final."""

    if VERDICT_FREEZE.exists():
        raise SystemExit("verdict_freeze.json já existe; o congelamento não é refeito.")
    check_datasets()
    models = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False).stdout
    payload = {
        "frozen_at": time.strftime("%Y-%m-%d"),
        "conditions": list(FINAL_CONDITIONS),
        "datasets": list(DATASETS),
        "sha256": file_hashes(),
        "ollama_models": [
            " ".join(line.split()[:2])
            for line in models.splitlines()[1:]
            if line.split()[:1] == ["qwen3:8b"]
        ],
    }
    VERDICT_FREEZE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Congelamento gravado em {VERDICT_FREEZE.relative_to(REPOSITORY)}.")


def verify_freeze() -> None:
    if not VERDICT_FREEZE.is_file():
        raise SystemExit("A fase final exige verdict_freeze.json gravado antes (--write-freeze).")
    frozen = json.loads(VERDICT_FREEZE.read_text("utf-8"))["sha256"]
    changed = [name for name, digest in file_hashes().items() if frozen.get(name) != digest]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))
    check_datasets()


def c7_cases(split: str) -> list[dict]:
    rows = [json.loads(line) for line in C7_ITEMS.read_text("utf-8").splitlines() if line]
    return [
        {
            "case_id": row["item_id"],
            "claim": row["claim"],
            "claim_family": row["claim_family"],
            "expected_label": row["label"],
            "split": row["split"],
            "origin_type": row["origin_type"],
            "misleading_subtype": row["misleading_subtype"],
            "source_chunk_id": row["source_chunk_id"],
        }
        for row in rows
        if row["split"] == split
    ]


def external2_cases() -> list[dict]:
    rows = [json.loads(line) for line in EXTERNAL2_ITEMS.read_text("utf-8").splitlines() if line]
    return [
        {
            "case_id": row["item_id"],
            "claim": row["claim"],
            "claim_family": row["claim_family"],
            "expected_label": row["label"],
            "split": "external2",
            "corpus_topic_coverage": row.get("corpus_topic_coverage"),
            "external_flags": row.get("external_flags", []),
            "external_agency": row.get("external_agency"),
        }
        for row in sorted(rows, key=lambda item: item["item_id"])
    ]


def build_pipeline(condition: str, trace_sink):
    """`v3`, `v5_fixed`, `C6` (cascata, ADR-055) ou `v7+C1+...` (candidatas sobre a `v5_fixed`)."""

    if condition in BASELINES:
        return build_v6_pipeline(condition, trace_sink)
    if condition == "C6":
        return build_cascade_pipeline(trace_sink=trace_sink)
    name, *candidates = condition.split("+")
    if name != "v7":
        raise SystemExit(f"Condição desconhecida: {condition}")
    return build_v7_text_pipeline(candidates, trace_sink=trace_sink)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimento v7 (ADR-054 e ADR-055).")
    parser.add_argument("--write-freeze", action="store_true", help="grava verdict_freeze.json")
    parser.add_argument(
        "--condition",
        help=f"v3, v5_fixed, C6 ou v7+<candidatas> (de {', '.join(CANDIDATES)})",
    )
    parser.add_argument("--phase", choices=("dev", "final"), default="dev")
    parser.add_argument("--dataset", choices=DATASETS, default="c7")
    parser.add_argument("--limit", type=int, help="só os primeiros N casos (somente na fase dev)")
    parser.add_argument("--tag", default="run1")
    args = parser.parse_args()

    if args.write_freeze:
        write_freeze()
        return
    if not args.condition:
        parser.error("--condition é obrigatório.")
    if args.phase == "dev":
        if args.dataset != "c7":
            parser.error("Na fase dev só o desenvolvimento do C7 pode ser usado.")
        cases = c7_cases("development")
        name = f"{args.condition.replace('+', '_')}_c7_development_{args.tag}"
    else:
        if args.condition not in FINAL_CONDITIONS:
            parser.error(f"Na fase final só valem {', '.join(FINAL_CONDITIONS)}.")
        if args.limit:
            parser.error("A fase final roda o conjunto inteiro.")
        verify_freeze()
        cases = c7_cases("test") if args.dataset == "c7" else external2_cases()
        name = f"{args.condition}_{args.dataset}_final"
    if args.limit:
        cases = cases[: args.limit]

    output_dir = RUNS / args.phase
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / f"{name}.jsonl"
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
