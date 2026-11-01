"""Agrega as respostas do formulário de avaliação por testadores (docs/USABILITY_QUESTIONNAIRE.md).

Lê a planilha exportada do Google Forms (.xlsx), guardada fora do repositório, e grava só agregados
em `evaluation/usability/results.json`: SUS por respondente e resumo, distribuições das perguntas
fechadas e contagens. Respostas abertas e carimbos de data/hora não são gravados.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import unicodedata
import zipfile
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from xml.etree import ElementTree

REPOSITORY = Path(__file__).resolve().parents[1]
REPORT = REPOSITORY / "evaluation/usability/results.json"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
LIKERT = {
    "explicacao_clara": "explicação das respostas foi fácil",
    "fontes_confiaveis": "fontes apresentadas pareceram",
    "tempo_aceitavel": "tempo de espera",
    "orientacao_insuficiente_util": "evidência insuficiente",
    "confiaria_para_compartilhar": "confiaria no veredito",
    "vereditos_corretos": "vereditos recebidos pareceram",
}
CATEGORICAL = {
    "faixa_etaria": "faixa etária",
    "area_saude": "área da saúde",
    "frequencia_mensagens": "com que frequência",
    "alegacoes_enviadas": "quantas alegações",
    "tipos_conteudo": "tipos de conteúdo",
    "envio_com_erro": "terminou sem resposta",
    "abriu_fonte": "abriu algum link",
}


def _plain(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def read_xlsx(path: Path) -> list[list[str]]:
    """Lê a primeira planilha de um .xlsx só com a biblioteca padrão."""
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(NS + "t")) for si in root]
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.find(NS + "sheetData"):
        cells: dict[int, str] = {}
        for cell in row:
            letters = re.match(r"[A-Z]+", cell.get("r")).group()
            index = 0
            for letter in letters:
                index = index * 26 + ord(letter) - 64
            value = cell.find(NS + "v")
            if cell.get("t") == "s":
                text = shared[int(value.text)]
            elif cell.get("t") == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(NS + "t"))
            else:
                text = value.text if value is not None else ""
            cells[index - 1] = text.strip()
        rows.append([cells.get(i, "") for i in range(max(cells, default=-1) + 1)])
    return rows


def _column(header: list[str], fragment: str) -> int:
    matches = [i for i, name in enumerate(header) if _plain(fragment) in _plain(name)]
    if len(matches) != 1:
        raise SystemExit(f"Coluna não identificada sem ambiguidade: {fragment!r}")
    return matches[0]


def _score(value: str) -> int | None:
    """'5.0', '5' ou '5 — Concordo totalmente' viram 5; 'Não recebi essa resposta' vira None."""
    match = re.match(r"\s*([1-5])(?:\.0)?\b", value)
    return int(match.group(1)) if match else None


def _category(value: str) -> str:
    return "1" if value == "1.0" else value  # o Sheets converte a opção "1" em número


def sus(answers: list[int]) -> float:
    """Pontuação SUS (Brooke, 1996): ímpares valem resposta − 1; pares, 5 − resposta; soma × 2,5."""
    total = sum(a - 1 if n % 2 else 5 - a for n, a in enumerate(answers, start=1))
    return total * 2.5


def _summary(values: list[float]) -> dict[str, float]:
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 1),
        "sd": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
        "median": round(statistics.median(values), 1),
        "min": min(values),
        "max": max(values),
    }


def analyze(rows: list[list[str]]) -> dict[str, object]:
    header, data = rows[0], [r + [""] * (len(rows[0]) - len(r)) for r in rows[1:] if any(r)]
    consent = _column(header, "concorda em participar")
    adult = _column(header, "18 anos ou mais")
    data = [r for r in data if r[consent].startswith("Sim") and r[adult] == "Sim"]
    sus_columns = [_column(header, f"{n}. Eu ") for n in range(1, 11)]
    stamps = [float(r[_column(header, "carimbo")]) for r in data]

    scores = []
    straightlined = []
    for number, row in enumerate(data, start=1):
        answers = [_score(row[c]) for c in sus_columns]
        if None in answers:
            raise SystemExit(f"Respondente {number}: item do SUS sem resposta numérica.")
        scores.append(sus(answers))
        if len(set(answers)) == 1:
            straightlined.append(number)

    report: dict[str, object] = {
        "n": len(data),
        "collection_period": [
            str(date(1899, 12, 30) + timedelta(days=int(min(stamps)))),
            str(date(1899, 12, 30) + timedelta(days=int(max(stamps)))),
        ],
        "sus": {
            "scores": scores,
            **_summary(scores),
            "above_68": sum(s > 68 for s in scores),
            "straightlined_respondents": straightlined,
        },
    }
    if straightlined:
        kept = [s for i, s in enumerate(scores, start=1) if i not in straightlined]
        report["sus"]["without_straightlined"] = _summary(kept)
    report["likert"] = {}
    for key, fragment in LIKERT.items():
        column = _column(header, fragment)
        values = [_score(r[column]) for r in data]
        numeric = [v for v in values if v is not None]
        report["likert"][key] = {
            "distribution": {str(p): numeric.count(p) for p in range(1, 6)},
            "not_applicable": values.count(None),
            "agree_4_or_5": sum(v >= 4 for v in numeric),
            "median": statistics.median(numeric) if numeric else None,
        }
    report["profile"] = {}
    for key, fragment in CATEGORICAL.items():
        column = _column(header, fragment)
        counts: Counter[str] = Counter()
        for row in data:
            options = row[column].split(", ") if key == "tipos_conteudo" else [row[column]]
            counts.update(_category(option) for option in options)
        report["profile"][key] = dict(sorted(counts.items()))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Agregados do formulário de testadores.")
    parser.add_argument("xlsx", type=Path, help="planilha exportada, fora do repositório")
    parser.add_argument("--write", action="store_true", help=f"grava {REPORT.name}")
    args = parser.parse_args()
    if REPOSITORY in args.xlsx.resolve().parents:
        raise SystemExit("A planilha bruta deve ficar fora do repositório.")
    text = json.dumps(analyze(read_xlsx(args.xlsx)), ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
