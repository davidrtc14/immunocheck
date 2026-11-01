"""Execução única da linha de base sem recuperação (ADR-058) no teste do C7 e no teste externo 2.

O Qwen3-8B decide sozinho (`closed_book.py`), com o mesmo cliente, temperatura e semente da v7. Exige
`evaluation/no_rag/freeze.json`, gravado com `--write-freeze` antes da execução, e confere os mesmos
conjuntos congelados da Fase 20. Registros retomáveis fora do Git, em `output/no_rag_runs/`, porque
contêm explicações sobre alegações das agências.
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

from run_v7_experiment import (  # type: ignore[import-not-found]
    c7_cases,
    check_datasets,
    external2_cases,
)

from immunocheck.application.closed_book import ClosedBookPipeline
from immunocheck.bootstrap import _build_llm_client
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict

REPOSITORY = Path(__file__).resolve().parents[1]
FREEZE = REPOSITORY / "evaluation/no_rag/freeze.json"
RUNS = REPOSITORY / "output/no_rag_runs"
CONDITION = "no_rag"
DATASETS = ("c7", "external2")
FROZEN_FILES = (
    "scripts/run_no_rag_baseline.py",
    "scripts/analyze_no_rag.py",
    "src/immunocheck/application/closed_book.py",
    "src/immunocheck/bootstrap.py",
    "src/immunocheck/infrastructure/ollama.py",
    "src/immunocheck/infrastructure/context_budget.py",
    "evaluation/no_rag/PROTOCOL.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def file_hashes() -> dict[str, str]:
    return {name: _sha256(REPOSITORY / name) for name in FROZEN_FILES}


def write_freeze() -> None:
    if FREEZE.exists():
        raise SystemExit("freeze.json já existe; o congelamento não é refeito.")
    check_datasets()
    models = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False).stdout
    payload = {
        "frozen_at": time.strftime("%Y-%m-%d"),
        "condition": CONDITION,
        "datasets": list(DATASETS),
        "sha256": file_hashes(),
        "ollama_models": [
            " ".join(line.split()[:2])
            for line in models.splitlines()[1:]
            if line.split()[:1] == ["qwen3:8b"]
        ],
    }
    FREEZE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Congelamento gravado em {FREEZE.relative_to(REPOSITORY)}.")


def verify_freeze() -> None:
    if not FREEZE.is_file():
        raise SystemExit("A execução exige evaluation/no_rag/freeze.json (--write-freeze).")
    frozen = json.loads(FREEZE.read_text("utf-8"))["sha256"]
    changed = [name for name, digest in file_hashes().items() if frozen.get(name) != digest]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))
    check_datasets()


def main() -> None:
    parser = argparse.ArgumentParser(description="Linha de base sem recuperação (ADR-058).")
    parser.add_argument("--write-freeze", action="store_true", help="grava freeze.json")
    parser.add_argument("--dataset", choices=DATASETS)
    args = parser.parse_args()
    if args.write_freeze:
        write_freeze()
        return
    if not args.dataset:
        parser.error("--dataset é obrigatório.")
    verify_freeze()
    cases = c7_cases("test") if args.dataset == "c7" else external2_cases()

    RUNS.mkdir(parents=True, exist_ok=True)
    checkpoint = RUNS / f"{CONDITION}_{args.dataset}.jsonl"
    done: set[str] = set()
    if checkpoint.exists():
        done = {
            json.loads(line)["case_id"]
            for line in checkpoint.read_text("utf-8").splitlines()
            if line
        }
        if len(done) >= len(cases):
            raise SystemExit("Esta execução já foi concluída; não se repete.")

    pipeline = ClosedBookPipeline(_build_llm_client(model=None, base_url=None))
    with checkpoint.open("a", encoding="utf-8", newline="\n") as handle:
        for case in cases:
            if case["case_id"] in done:
                continue
            started = time.perf_counter()
            failure, explanation = None, None
            try:
                result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=case["claim"]))
                verdict, explanation = result.verdict.value, result.explanation
            except Exception as exc:  # noqa: BLE001 - falha técnica é dado do experimento
                verdict, failure = Verdict.INSUFFICIENT_EVIDENCE.value, type(exc).__name__
            record = {key: value for key, value in case.items() if key != "claim"}
            record.update(
                verdict=verdict,
                source_ids=[],
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                failure=failure,
                explanation=explanation,
            )
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(case["case_id"], "->", verdict, failure or "", flush=True)


if __name__ == "__main__":
    main()
