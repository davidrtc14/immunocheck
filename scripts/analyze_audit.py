"""Analisa a auditoria humana da v7: proporções por avaliador, concordância e kappa de Cohen.

Lê `output/audit/avaliador_A.csv` e `avaliador_B.csv`, preenchidas de forma independente
(evaluation/audit/PROTOCOL.md), e grava só agregados em `evaluation/audit/results.json`.
"""

from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
OUTPUT = REPOSITORY / "output/audit"
REPORT = REPOSITORY / "evaluation/audit/results.json"
CATEGORIES = ("sim", "parcial", "nao")
QUESTIONS = {
    "explicacao_correta": "A explicação está correta? (Sim/Parcial/Não)",
    "fontes_sustentam": "As fontes sustentam a explicação? (Sim/Parcial/Não)",
}


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().strip().lower()
    if text not in CATEGORIES:
        raise ValueError(f"Resposta inválida na planilha: {value!r} (use Sim, Parcial ou Não).")
    return text


def read(evaluator: str) -> dict[str, dict[str, str]]:
    path = OUTPUT / f"avaliador_{evaluator}.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    return {
        row["ID"]: {key: normalize(row[column]) for key, column in QUESTIONS.items()}
        for row in rows
    }


def cohen_kappa(first: list[str], second: list[str]) -> float | None:
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / n
    count_a, count_b = Counter(first), Counter(second)
    expected = sum(count_a[c] * count_b[c] for c in CATEGORIES) / (n * n)
    if expected == 1:
        return None  # sem variação: o kappa não é definido
    return (observed - expected) / (1 - expected)


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria humana da v7.")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()
    first, second = read("A"), read("B")
    if first.keys() != second.keys():
        raise SystemExit("As duas planilhas devem ter os mesmos IDs.")
    ids = sorted(first)
    report: dict[str, object] = {"n": len(ids)}
    for key in QUESTIONS:
        a = [first[i][key] for i in ids]
        b = [second[i][key] for i in ids]
        kappa = cohen_kappa(a, b)
        report[key] = {
            "A": {c: a.count(c) for c in CATEGORIES},
            "B": {c: b.count(c) for c in CATEGORIES},
            "observed_agreement": round(
                sum(x == y for x, y in zip(a, b, strict=True)) / len(ids), 3
            ),
            "cohen_kappa": None if kappa is None else round(kappa, 3),
            "disagreements": [i for i, x, y in zip(ids, a, b, strict=True) if x != y],
        }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
