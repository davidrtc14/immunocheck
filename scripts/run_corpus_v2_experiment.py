"""Executa a C6 com o corpus v2 no teste do C7 ou no teste externo 2 (Fase 21, ADR-056).

Execução única, como no protocolo de `evaluation/corpus_v2/PROTOCOL.md`. A pipeline é a mesma da
Fase 20, montada pelo executor congelado da v7; muda só o corpus em `corpus/processed/`. Antes de
rodar, o script confere o congelamento da Fase 20 (o código não pode ter mudado), o congelamento
desta fase (corpus v2, executor, análise e protocolo) e os conjuntos. Os registros ficam fora do Git
em `output/corpus_v2_runs/`, porque os traces contêm trechos do corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_v7_experiment import (  # type: ignore[import-not-found]
    _sha256,
    build_pipeline,
    c7_cases,
    external2_cases,
)
from run_v7_experiment import (
    verify_freeze as verify_v7_freeze,
)

from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict

REPOSITORY = Path(__file__).resolve().parents[1]
FREEZE = REPOSITORY / "evaluation/corpus_v2/freeze.json"
RUNS = REPOSITORY / "output/corpus_v2_runs"
CONDITION = "C6"
DATASETS = ("c7", "external2")
FROZEN_FILES = (
    "scripts/run_corpus_v2_experiment.py",
    "scripts/analyze_corpus_v2.py",
    "evaluation/corpus_v2/PROTOCOL.md",
    "corpus/catalog.csv",
    "corpus/reviews/batch_009.csv",
)
# Artefatos binários ou gerados localmente: hash dos bytes exatos, sem normalizar quebras de linha.
CORPUS_FILES = (
    "corpus/processed/chunks.jsonl",
    "corpus/processed/manifest.json",
    "corpus/processed/dense_bge_m3.npz",
    "corpus/processed/dense_bge_m3.json",
)


def _raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_hashes() -> dict[str, str]:
    hashes = {name: _sha256(REPOSITORY / name) for name in FROZEN_FILES}
    hashes.update({name: _raw_sha256(REPOSITORY / name) for name in CORPUS_FILES})
    return hashes


def write_freeze() -> None:
    if FREEZE.exists():
        raise SystemExit("freeze.json já existe; o congelamento não é refeito.")
    verify_v7_freeze()
    manifest = json.loads((REPOSITORY / "corpus/processed/manifest.json").read_text("utf-8"))
    payload = {
        "frozen_at": time.strftime("%Y-%m-%d"),
        "condition": CONDITION,
        "datasets": list(DATASETS),
        "corpus_version": manifest["corpus_version"],
        "sha256": file_hashes(),
    }
    FREEZE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Congelamento gravado em {FREEZE.relative_to(REPOSITORY)}.")


def verify_freeze() -> None:
    if not FREEZE.is_file():
        raise SystemExit("A execução exige evaluation/corpus_v2/freeze.json (--write-freeze).")
    verify_v7_freeze()
    frozen = json.loads(FREEZE.read_text("utf-8"))["sha256"]
    changed = [name for name, digest in file_hashes().items() if frozen.get(name) != digest]
    if changed:
        raise SystemExit("Congelamento violado: " + ", ".join(changed))


def main() -> None:
    parser = argparse.ArgumentParser(description="Execução única da C6 com o corpus v2 (ADR-056).")
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
    checkpoint = RUNS / f"{CONDITION}_{args.dataset}_corpus_v2.jsonl"
    done: set[str] = set()
    if checkpoint.exists():
        done = {
            json.loads(line)["case_id"]
            for line in checkpoint.read_text("utf-8").splitlines()
            if line
        }
        if len(done) >= len(cases):
            raise SystemExit("Esta execução já foi feita; não se repete.")

    traces: list[dict] = []
    pipeline = build_pipeline(CONDITION, traces.append)
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
    verify_freeze()


if __name__ == "__main__":
    main()
