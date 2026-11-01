"""Monta as planilhas da auditoria humana em Excel a partir de `output/audit/items.jsonl`.

Mesmo conteúdo das planilhas CSV de `build_audit_sample.py`, num formato legível: colunas largas com
quebra de linha, cabeçalho fixo e listas suspensas Sim/Parcial/Não nas colunas de avaliação. Não
chama o modelo; só reformata as respostas já geradas.
"""

from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from immunocheck.domain.models import Verdict
from immunocheck.presentation import VERDICT_LABELS

REPOSITORY = Path(__file__).resolve().parents[1]
OUTPUT = REPOSITORY / "output/audit"
MAX_EXCERPT = 1_500
COLUMNS = (
    ("ID", 7),
    ("Alegação", 35),
    ("Veredito", 13),
    ("Explicação", 50),
    ("Fato correto ou distorção apontada", 35),
    ("Fontes exibidas", 35),
    ("Texto dos trechos citados", 80),
    ("A explicação está correta? (Sim/Parcial/Não)", 16),
    ("As fontes sustentam a explicação? (Sim/Parcial/Não)", 16),
    ("Comentário", 35),
)
INSTRUCTIONS = (
    "Preencha sozinho, sem conversar com o outro avaliador até os dois terminarem.",
    "",
    "A explicação está correta?",
    "  Sim: tudo o que ela afirma é correto e coerente com o veredito.",
    "  Parcial: há imprecisão menor que não muda o veredito.",
    "  Não: há erro factual ou a explicação contradiz o veredito.",
    "",
    "As fontes sustentam a explicação?",
    "  Sim: os trechos citados afirmam o que a explicação diz.",
    "  Parcial: sustentam só parte.",
    "  Não: não tratam do que foi dito ou o contradizem.",
    "",
    "Comentário: opcional; obrigatório quando alguma resposta for Não.",
    "Use as listas suspensas das colunas H e I. Não mude a ordem nem os IDs das linhas.",
    "Avalie a resposta do bot, não se você concorda com o veredito: o gabarito não é mostrado.",
)


def _row(item: dict) -> list[str]:
    sources = item["sources"]
    return [
        item["audit_id"],
        item["claim"],
        VERDICT_LABELS[Verdict(item["verdict"])],
        item["explanation"],
        item["correct_fact"] or item["omitted_or_distorted"] or "",
        "\n".join(f"[{i}] {s['label']} ({s['url']})" for i, s in enumerate(sources, 1)),
        "\n\n".join(f"[{i}] {s['text'][:MAX_EXCERPT]}" for i, s in enumerate(sources, 1)),
        "",
        "",
        "",
    ]


def build(items: list[dict], path: Path) -> None:
    book = Workbook()
    sheet = book.active
    sheet.title = "Avaliação"
    sheet.append([name for name, _ in COLUMNS])
    for item in items:
        sheet.append(_row(item))
    header_fill = PatternFill("solid", fgColor="1F4E78")
    answer_fill = PatternFill("solid", fgColor="FFF2CC")
    for index, (_, width) in enumerate(COLUMNS, start=1):
        letter = sheet.cell(row=1, column=index).column_letter
        sheet.column_dimensions[letter].width = width
        cell = sheet.cell(row=1, column=index)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if cell.column >= 8:
                cell.fill = answer_fill
        sheet.row_dimensions[row[0].row].height = 300
    sheet.row_dimensions[1].height = 45
    sheet.freeze_panes = "B2"
    last = len(items) + 1
    choices = DataValidation(type="list", formula1='"Sim,Parcial,Não"', allow_blank=True)
    choices.error = "Escolha Sim, Parcial ou Não."
    sheet.add_data_validation(choices)
    choices.add(f"H2:I{last}")

    guide = book.create_sheet("Instruções", 0)
    guide.column_dimensions["A"].width = 100
    for line in INSTRUCTIONS:
        guide.append([line])
    guide["A1"].font = Font(bold=True)
    book.active = 1
    book.save(path)


def main() -> None:
    items = [
        json.loads(line)
        for line in (OUTPUT / "items.jsonl").read_text("utf-8").splitlines()
        if line
    ]
    for evaluator in ("A", "B"):
        build(items, OUTPUT / f"avaliador_{evaluator}.xlsx")
    print(f"{len(items)} itens em avaliador_A.xlsx e avaliador_B.xlsx.")


if __name__ == "__main__":
    main()
