"""Audita o release candidate local sem promover a branch nem expor segredos."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from immunocheck import __version__
from immunocheck.evaluation.benchmark_freeze import validate_freeze_manifest
from immunocheck.infrastructure.ocr import TesseractOCR
from immunocheck.release_readiness import summarize_readiness
from immunocheck.retrieval.dense import load_dense_index
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/release/release_preflight.json"
CORPUS_PATH = REPOSITORY / "corpus/processed/chunks.jsonl"
VECTORS_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.npz"
DENSE_MANIFEST_PATH = REPOSITORY / "corpus/processed/dense_bge_m3.json"
ROADMAP_PATH = REPOSITORY / "docs/ROADMAP.md"
FINAL_TEST_PATH = REPOSITORY / "evaluation/results/test/final_test.json"
PERFORMANCE_PATH = REPOSITORY / "evaluation/results/performance/operational_performance.json"
DEMO_PATH = REPOSITORY / "evaluation/results/demo/automated_rehearsal.json"
FROZEN_BENCHMARK_ROOT = REPOSITORY / "evaluation/end_to_end"


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    passed: bool
    required: bool
    detail: str
    duration_ms: float


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight local do release candidate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--with-tests", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("O preflight original já existe; use outro caminho para uma réplica.")

    checks = [
        _timed_check("python_version", True, _check_python),
        _timed_check("package_version", True, _check_package_version),
        _timed_check("git_branch", True, _check_git_branch),
        _timed_check("git_worktree_clean", True, _check_git_clean),
        _timed_check("git_develop_synced", True, _check_git_synced),
        _timed_check("tracked_file_policy", True, _check_tracked_files),
        _timed_check("benchmark_freeze", True, _check_benchmark_freeze),
        _timed_check("corpus_and_dense_index", True, _check_corpus_and_index),
        _timed_check("final_test_artifact", True, _check_final_test),
        _timed_check("performance_artifact", True, _check_performance),
        _timed_check("demo_artifact", True, _check_demo),
        _timed_check("ollama_model", True, _check_ollama),
        _timed_check("tesseract_portuguese", True, _check_tesseract),
        _timed_check("docker_engine", True, _check_docker),
        _timed_check("docker_compose", True, _check_compose),
        _timed_check("postgres_health", True, _check_postgres),
    ]
    if args.with_tests:
        checks.extend(
            (
                _timed_check("ruff", True, _check_ruff),
                _timed_check("pytest", True, _check_pytest),
            )
        )

    roadmap = ROADMAP_PATH.read_text("utf-8")
    human_gates = [
        {
            "name": "institutional_lgpd_cep_decision",
            "completed": _checked(
                roadmap,
                "Definição institucional de papéis, base legal, canal do titular e CEP/CONEP quando aplicável.",
            ),
            "evidence_expected": "docs/INSTITUTIONAL_GATE_PACKAGE.md preenchido e síntese desidentificada",
        },
        {
            "name": "live_bot_presentation_rehearsal",
            "completed": _checked(
                roadmap,
                "Ensaio ao vivo com o bot e o ambiente que serão usados na apresentação.",
            ),
            "evidence_expected": "registro desidentificado do checklist de demonstração",
        },
    ]
    serialized_checks = [asdict(check) for check in checks]
    summary = summarize_readiness(serialized_checks, human_gates)
    result = {
        "schema_version": 1,
        "purpose": "local_release_candidate_preflight",
        "executed_at": datetime.now(UTC).isoformat(),
        "commit": _git("rev-parse", "HEAD"),
        "branch": _git("branch", "--show-current"),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "package_version": __version__,
        },
        "tests_requested": args.with_tests,
        "checks": serialized_checks,
        "human_gates": human_gates,
        "summary": summary,
        "promotion_performed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Preflight salvo em {args.output.relative_to(REPOSITORY)}")
    if not summary["technical_ready"]:
        raise SystemExit(1)


def _timed_check(name: str, required: bool, function: Any) -> Check:
    started = time.perf_counter()
    try:
        passed, detail = function()
    except Exception as exc:  # noqa: BLE001 - o relatório deve registrar toda falha técnica
        passed, detail = False, f"{type(exc).__name__}: verificação indisponível"
    return Check(
        name=name,
        passed=bool(passed),
        required=required,
        detail=str(detail),
        duration_ms=(time.perf_counter() - started) * 1_000,
    )


def _check_python() -> tuple[bool, str]:
    version = platform.python_version()
    return version.startswith("3.12."), f"Python {version}"


def _check_package_version() -> tuple[bool, str]:
    project = tomllib.loads((REPOSITORY / "pyproject.toml").read_text("utf-8"))["project"]
    declared = str(project["version"])
    return __version__ == declared, f"pacote {__version__}; pyproject {declared}"


def _check_git_branch() -> tuple[bool, str]:
    branch = _git("branch", "--show-current")
    return branch == "develop", f"branch {branch}"


def _check_git_clean() -> tuple[bool, str]:
    clean = not _git("status", "--porcelain")
    return clean, "worktree limpo" if clean else "worktree possui alterações"


def _check_git_synced() -> tuple[bool, str]:
    head = _git("rev-parse", "HEAD")
    upstream = _git("rev-parse", "origin/develop")
    return head == upstream, "HEAD coincide com origin/develop" if head == upstream else "branch não sincronizada"


def _check_tracked_files() -> tuple[bool, str]:
    tracked = set(_git("ls-files").splitlines())
    forbidden = sorted(
        path
        for path in tracked
        if path == ".env"
        or path.startswith(("corpus/raw/", "corpus/processed/", "models/", "data/private/"))
        or path.endswith((".db", ".sqlite", ".sqlite3", ".log"))
    )
    return not forbidden, "nenhum segredo ou artefato privado versionado" if not forbidden else f"arquivos proibidos: {len(forbidden)}"


def _check_benchmark_freeze() -> tuple[bool, str]:
    manifest = validate_freeze_manifest(root=FROZEN_BENCHMARK_ROOT)
    return manifest["test_frozen"] is True, str(manifest["freeze_id"])


def _check_corpus_and_index() -> tuple[bool, str]:
    evidence = load_evidence_jsonl(CORPUS_PATH)
    _, manifest = load_dense_index(
        evidence=evidence,
        vectors_path=VECTORS_PATH,
        manifest_path=DENSE_MANIFEST_PATH,
        corpus_path=CORPUS_PATH,
    )
    return len(evidence) > 0, f"{len(evidence)} chunks; modelo {manifest.model_name}"


def _check_final_test() -> tuple[bool, str]:
    value = _read_json(FINAL_TEST_PATH)
    passed = (
        value.get("post_test_changes_allowed") is False
        and value.get("partition") == "test"
        and value.get("test_items_loaded") == 64
    )
    return passed, "teste único preservado; 64 itens"


def _check_performance() -> tuple[bool, str]:
    value = _read_json(PERFORMANCE_PATH)
    summaries = value.get("summaries", {})
    passed = (
        value.get("post_test_tuning_performed") is False
        and all(summaries.get(name, {}).get("runs") == 30 for name in ("image", "link", "telegram_feedback"))
        and summaries.get("image", {}).get("technical_failures") == 0
        and summaries.get("link", {}).get("technical_failures") == 0
    )
    return passed, "90 medições controladas; zero falhas de imagem/link"


def _check_demo() -> tuple[bool, str]:
    value = _read_json(DEMO_PATH)
    passed = value.get("all_passed") is True and value.get("live_telegram_used") is False
    return passed, "4/4 cenários locais aprovados; sem Telegram real"


def _check_ollama() -> tuple[bool, str]:
    executable = _resolve_executable(
        "ollama",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Ollama/ollama.exe",
    )
    result = _run((executable, "list"), timeout=20)
    passed = result.returncode == 0 and "qwen3:8b" in result.stdout.lower()
    return passed, "qwen3:8b disponível localmente" if passed else "qwen3:8b não detectado"


def _check_tesseract() -> tuple[bool, str]:
    executable = TesseractOCR.from_environment().executable
    result = _run((str(executable), "--list-langs"), timeout=20)
    passed = result.returncode == 0 and "por" in {line.strip() for line in result.stdout.splitlines()}
    return passed, "Tesseract com idioma por" if passed else "idioma por não detectado"


def _check_docker() -> tuple[bool, str]:
    executable = _docker_executable()
    result = _run((executable, "version", "--format", "{{.Server.Version}}"), timeout=20)
    version = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "indisponível"
    return result.returncode == 0, f"Docker Server {version}"


def _check_compose() -> tuple[bool, str]:
    executable = _docker_executable()
    result = _run((executable, "compose", "version", "--short"), timeout=20)
    version = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "indisponível"
    return result.returncode == 0, f"Docker Compose {version}"


def _check_postgres() -> tuple[bool, str]:
    executable = _docker_executable()
    result = _run(
        (
            executable,
            "compose",
            "exec",
            "-T",
            "postgres",
            "pg_isready",
            "-U",
            "immunocheck",
            "-d",
            "immunocheck",
        ),
        timeout=20,
    )
    return result.returncode == 0, "PostgreSQL respondeu pg_isready" if result.returncode == 0 else "PostgreSQL indisponível"


def _check_ruff() -> tuple[bool, str]:
    result = _run((sys.executable, "-m", "ruff", "check", "src", "scripts", "tests"), timeout=120)
    return result.returncode == 0, "Ruff aprovado" if result.returncode == 0 else "Ruff encontrou apontamentos"


def _check_pytest() -> tuple[bool, str]:
    result = _run(
        (
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--basetemp",
            "output/release-preflight-pytest",
            "-p",
            "no:cacheprovider",
        ),
        timeout=300,
    )
    passed = result.returncode == 0
    summary = next(
        (line.strip() for line in reversed(result.stdout.splitlines()) if " passed" in line),
        "pytest sem resumo disponível",
    )
    return passed, summary if passed else "pytest falhou"


def _checked(roadmap: str, label: str) -> bool:
    return f"- [x] {label}" in roadmap


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Artefato JSON inválido.")
    return value


def _docker_executable() -> str:
    return _resolve_executable(
        "docker",
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Programs/DockerDesktop/resources/bin/docker.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "Docker/Docker/resources/bin/docker.exe",
    )


def _resolve_executable(name: str, *candidates: Path) -> str:
    discovered = shutil.which(name)
    if discovered:
        return discovered
    for candidate in candidates:
        try:
            if candidate.is_file():
                return str(candidate)
        except OSError:
            continue
    raise FileNotFoundError(f"Executável {name} não encontrado.")


def _git(*arguments: str) -> str:
    result = _run(("git", *arguments), timeout=30)
    if result.returncode != 0:
        raise RuntimeError("Comando Git falhou.")
    return result.stdout.strip()


def _run(command: tuple[str, ...], *, timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


if __name__ == "__main__":
    main()
