"""Congela a candidata v4 (v3 + D1) com hashes de código, dados, corpus, índice e modelo."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

REPOSITORY = Path(__file__).resolve().parents[1]
FREEZE = REPOSITORY / "evaluation/refinement_v4/holdout_freeze.json"
FILES = (
    "src/immunocheck/application/text_components.py",
    "src/immunocheck/application/routed_pipeline.py",
    "src/immunocheck/application/grounding.py",
    "src/immunocheck/application/advice_guard.py",
    "src/immunocheck/application/abstention.py",
    "src/immunocheck/retrieval/document_expansion.py",
    "src/immunocheck/infrastructure/context_budget.py",
    "evaluation/refinement_v4/items.jsonl",
    "evaluation/refinement_v4/HOLDOUT_PROTOCOL.md",
    "corpus/processed/chunks.jsonl",
    "corpus/processed/dense_bge_m3.json",
    "corpus/processed/dense_bge_m3.npz",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def current_hashes() -> dict[str, str]:
    return {name: sha256(REPOSITORY / name) for name in FILES}


def ollama_digest(model: str = "qwen3:8b") -> str:
    opener = build_opener(ProxyHandler({}))
    with opener.open("http://127.0.0.1:11434/api/tags", timeout=10) as response:
        models = json.load(response)["models"]
    return next(item["digest"] for item in models if item["name"] == model)


def main() -> None:
    parser = argparse.ArgumentParser(description="Congela a candidata v4 antes do holdout.")
    parser.add_argument("--created-at", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if FREEZE.exists() and not args.overwrite:
        parser.error("Congelamento já existe; alterá-lo invalida o holdout.")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=REPOSITORY
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", "src", "evaluation/refinement_v4", "scripts"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPOSITORY,
    ).stdout.strip()
    if dirty:
        parser.error("Há alterações não commitadas em src/evaluation/scripts; commite antes.")
    freeze = {
        "schema_version": 1,
        "created_at": args.created_at,
        "candidate": "v3 + D1 (ancoragem verificável); sem D2 e sem D4/D5",
        "pipeline": {"grounded": True, "d4": False, "thresholds": "desativados"},
        "baseline": "v3 (prompts congelados), sem ancoragem",
        "git_commit": commit,
        "ollama_model": "qwen3:8b",
        "ollama_digest": ollama_digest(),
        "temperature": 0,
        "seed": 42,
        "num_ctx": 8192,
        "sha256": current_hashes(),
        "holdout_executed": False,
    }
    FREEZE.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(freeze, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
