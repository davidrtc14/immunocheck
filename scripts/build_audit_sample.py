"""Sorteia e gera as respostas da auditoria humana da v7 (evaluation/audit/PROTOCOL.md).

Sorteia, com semente 42, itens com veredito conclusivo da execução única de 20/10 (30 do teste do C7
e 15 do teste externo 2), gera de novo a resposta de cada um com a v7 padrão do bot e monta duas
planilhas idênticas, uma por avaliador, com a alegação, a resposta e o texto dos trechos citados.
Tudo fica em `output/audit/`, fora do Git: há trechos do corpus e alegações das agências.
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_v7_experiment import c7_cases, external2_cases  # type: ignore[import-not-found]

from immunocheck.bootstrap import DEFAULT_CORPUS_PATH
from immunocheck.bootstrap_bot import build_bot_text_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, Verdict
from immunocheck.presentation import VERDICT_LABELS

REPOSITORY = Path(__file__).resolve().parents[1]
RUNS = REPOSITORY / "output/v7_runs/final"
OUTPUT = REPOSITORY / "output/audit"
SEED = 42
QUOTAS = {
    ("c7", "SUPPORTED"): 10,
    ("c7", "REFUTED"): 10,
    ("c7", "MISLEADING"): 10,
    ("external2", "REFUTED"): 13,
    ("external2", "MISLEADING"): 2,
}
MAX_EXCERPT = 1_500
QUESTION_COLUMNS = (
    "A explicação está correta? (Sim/Parcial/Não)",
    "As fontes sustentam a explicação? (Sim/Parcial/Não)",
    "Comentário",
)


def _records(dataset: str) -> list[dict]:
    path = RUNS / f"C6_{dataset}_final.jsonl"
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def _chunks() -> dict[str, dict]:
    rows = (
        json.loads(line) for line in DEFAULT_CORPUS_PATH.read_text("utf-8").splitlines() if line
    )
    return {row["chunk_id"]: row for row in rows}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    claims = {case["case_id"]: case["claim"] for case in c7_cases("test") + external2_cases()}
    chunks = _chunks()
    pipeline = build_bot_text_pipeline()
    rng = random.Random(SEED)
    items: list[dict] = []
    for (dataset, verdict), quota in QUOTAS.items():
        pool = sorted(
            (row for row in _records(dataset) if row["verdict"] == verdict),
            key=lambda row: row["case_id"],
        )
        rng.shuffle(pool)
        taken = 0
        for row in pool:
            if taken == quota:
                break
            claim = claims[row["case_id"]]
            result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=claim))
            print(dataset, row["case_id"], verdict, "->", result.verdict.value, flush=True)
            if result.verdict is Verdict.INSUFFICIENT_EVIDENCE:
                continue
            taken += 1
            items.append(
                {
                    "dataset": dataset,
                    "case_id": row["case_id"],
                    "expected_label": row["expected_label"],
                    "original_verdict": verdict,
                    "verdict": result.verdict.value,
                    "claim": claim,
                    "explanation": result.explanation,
                    "correct_fact": result.correct_fact,
                    "omitted_or_distorted": result.omitted_or_distorted,
                    "sources": [
                        {
                            "chunk_id": source.chunk_id,
                            "label": " — ".join(
                                part
                                for part in (
                                    source.source_name,
                                    source.document_title,
                                    source.publication_date,
                                    source.section
                                    or (f"p. {source.page}" if source.page else None),
                                )
                                if part
                            ),
                            "url": source.url,
                            "text": chunks.get(source.chunk_id, {}).get("text", ""),
                        }
                        for source in result.sources
                    ],
                }
            )
        if taken < quota:
            print(f"Aviso: só {taken} de {quota} itens em {dataset}/{verdict}.", flush=True)

    rng.shuffle(items)
    for number, item in enumerate(items, start=1):
        item["audit_id"] = f"A{number:02d}"
    with (OUTPUT / "items.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for item in items:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    header = (
        "ID",
        "Alegação",
        "Veredito",
        "Explicação",
        "Fato correto ou distorção apontada",
        "Fontes exibidas",
        "Texto dos trechos citados",
        *QUESTION_COLUMNS,
    )
    for evaluator in ("A", "B"):
        with (OUTPUT / f"avaliador_{evaluator}.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(header)
            for item in items:
                sources = item["sources"]
                writer.writerow(
                    (
                        item["audit_id"],
                        item["claim"],
                        VERDICT_LABELS[Verdict(item["verdict"])],
                        item["explanation"],
                        item["correct_fact"] or item["omitted_or_distorted"] or "",
                        "\n".join(
                            f"[{i}] {s['label']} ({s['url']})" for i, s in enumerate(sources, 1)
                        ),
                        "\n\n".join(
                            f"[{i}] {s['text'][:MAX_EXCERPT]}" for i, s in enumerate(sources, 1)
                        ),
                        "",
                        "",
                        "",
                    )
                )
    print(f"{len(items)} itens em {OUTPUT.relative_to(REPOSITORY)}.")


if __name__ == "__main__":
    main()
