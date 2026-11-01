"""Analisa a auditoria humana da v7: proporções por avaliador, concordância e kappa de Cohen.

Lê `output/audit/avaliador_A.xlsx` e `avaliador_B.xlsx` (ou as versões .csv), preenchidas de forma independente
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


def _rows(evaluator: str) -> list[dict[str, str]]:
    path = OUTPUT / f"avaliador_{evaluator}.xlsx"
    if path.exists():
        from openpyxl import load_workbook

        values = list(load_workbook(path, read_only=True)["Avaliação"].iter_rows(values_only=True))
        header = [str(name) for name in values[0]]
        return [
            {
                name: "" if cell is None else str(cell)
                for name, cell in zip(header, row, strict=True)
            }
            for row in values[1:]
            if row[0]
        ]
    with (OUTPUT / f"avaliador_{evaluator}.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def read(evaluator: str) -> dict[str, dict[str, str]]:
    rows = _rows(evaluator)
    return {
        row["ID"]: {key: normalize(row[column]) for key, column in QUESTIONS.items()}
        for row in rows
    }


def cohen_kappa(
    first: list[str], second: list[str], categories: tuple[str, ...] = CATEGORIES
) -> float | None:
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / n
    count_a, count_b = Counter(first), Counter(second)
    expected = sum(count_a[c] * count_b[c] for c in categories) / (n * n)
    if expected == 1:
        return None  # sem variação: o kappa não é definido
    return (observed - expected) / (1 - expected)


def gwet_ac1(first: list[str], second: list[str], categories: tuple[str, ...]) -> float:
    """AC1 de Gwet (2008), menos sensível que o kappa a categorias dominantes (análise complementar)."""
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / n
    counts = Counter(first) + Counter(second)
    expected = sum(counts[c] / (2 * n) * (1 - counts[c] / (2 * n)) for c in categories) / (
        len(categories) - 1
    )
    return (observed - expected) / (1 - expected)


def complementary(first: list[str], second: list[str]) -> dict[str, object]:
    """Análise registrada depois do protocolo, por causa do paradoxo do kappa."""
    acceptable = ("aceitavel", "nao")
    a = ["aceitavel" if x != "nao" else "nao" for x in first]
    b = ["aceitavel" if x != "nao" else "nao" for x in second]
    return {
        "gwet_ac1": round(gwet_ac1(first, second, CATEGORIES), 3),
        "acceptable_vs_wrong": {
            "observed_agreement": round(sum(x == y for x, y in zip(a, b, strict=True)) / len(a), 3),
            "cohen_kappa": round(cohen_kappa(a, b, acceptable) or 0.0, 3),
            "gwet_ac1": round(gwet_ac1(a, b, acceptable), 3),
        },
    }


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
            "complementary_post_protocol": complementary(a, b),
        }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
