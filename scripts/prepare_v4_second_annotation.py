"""Gera o pacote cego de segunda anotação do v4: 12 famílias (6 por partição) = 50% dos itens."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from immunocheck.evaluation.end_to_end import DatasetSplit, EndToEndItem, load_end_to_end_items

REPOSITORY = Path(__file__).resolve().parents[1]
ITEMS = REPOSITORY / "evaluation/refinement_v4/items.jsonl"
CORPUS = REPOSITORY / "corpus/processed/chunks.jsonl"
OUTPUT = REPOSITORY / "evaluation/refinement_v4/second_annotation"
SEED = 20261013
FAMILIES_PER_SPLIT = 6

README = """# Instruções ao segundo anotador

Anote individualmente cada alegação de ANNOTATIONS.md, sem consultar rótulos do primeiro
anotador, pareceres do projeto ou respostas do ImmunoCheck. Não use LLM para substituir
seu julgamento. A ordem e os códigos foram embaralhados. Este é um benchmark acadêmico
controlado, com formulações sintéticas; não é uma amostra de mensagens reais nem um serviço
de aconselhamento médico.

1. Leia a proposição inteira, respeitando produto, população, território e data. Não
   complete dados ausentes.
2. Consulte diretamente os documentos listados em SOURCES.md (a lista cobre todos os temas do
   pacote e não indica qual documento sustenta qual alegação). Peça ao responsável o acesso ao
   snapshot local quando o documento não estiver disponível na web.
3. Preencha rótulo, justificativa própria, fontes e trechos/páginas. Para falta de evidência,
   descreva a informação ausente e a busca feita. Ausência de menção, por si só, não refuta.
   Não persiga uma distribuição de classes.
4. Registre dúvidas, tempo aproximado, data e um identificador interno sem nome civil nem
   e-mail. Devolva o formulário ao autor. Discordar é permitido: a concordância será calculada
   antes de qualquer discussão.

## Rótulos

| Rótulo | Critério |
| --- | --- |
| SUPPORTED | A evidência sustenta diretamente a proposição e seu escopo. |
| REFUTED | A evidência contradiz diretamente a proposição central. |
| MISLEADING | Há parte factual relevante sustentada, mas contexto, alcance ou inferência foi distorcido materialmente. Explicite ambas as partes. |
| INSUFFICIENT_EVIDENCE | O corpus não permite sustentar nem contradizer com segurança. Não significa verdadeiro nem falso. |
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Pacote de segunda anotação do v4.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        parser.error("Pacote já existe; use --overwrite somente para reprodução declarada.")

    items = load_end_to_end_items(ITEMS, require_reviewed=True)
    by_family: dict[str, list[EndToEndItem]] = defaultdict(list)
    for item in items:
        by_family[item.claim_family or ""].append(item)
    rng = random.Random(SEED)
    chosen_families: list[str] = []
    for split in DatasetSplit:
        names = sorted(f for f, group in by_family.items() if group[0].split is split)
        chosen_families += rng.sample(names, FAMILIES_PER_SPLIT)
    selected = [item for family in chosen_families for item in by_family[family]]
    rng.shuffle(selected)

    documents = sorted(
        {
            chunk.rsplit(":", 3)[0]
            for item in selected
            for chunk in item.evidence_chunk_ids
        }
    )
    catalog: dict[str, tuple[str, str]] = {}
    with CORPUS.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            if row["document_id"] in documents:
                catalog.setdefault(row["document_id"], (row["document_title"], row["url"]))

    participant = args.output / "participant"
    private = args.output / "private"
    participant.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    annotations = "# Formulário de anotação independente\n\nCampos vazios não contam como revisão.\n\n"
    mapping: dict[str, dict[str, str | None]] = {}
    for index, item in enumerate(selected, 1):
        task_id = f"annotation-{index:03d}"
        mapping[task_id] = {"item_id": item.item_id, "claim_family": item.claim_family}
        annotations += (
            f"## {task_id}\n\n{item.claim}\n\n"
            "- Rótulo:\n- Justificativa:\n- Fontes e trechos/páginas consultados:\n"
            "- Dúvidas ou ambiguidade:\n- Identificador interno do revisor:\n- Data:\n\n"
        )
    sources = "# Documentos do corpus a consultar\n\n" + "".join(
        f"- {title} — {url}\n" for _, (title, url) in sorted(catalog.items())
    )
    (participant / "README.md").write_text(README, encoding="utf-8", newline="\n")
    (participant / "ANNOTATIONS.md").write_text(annotations, encoding="utf-8", newline="\n")
    (participant / "SOURCES.md").write_text(sources, encoding="utf-8", newline="\n")
    (private / "selection_map.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "families": sorted(chosen_families),
                "item_count": len(selected),
                "fraction": len(selected) / len(items),
                "tasks": mapping,
                "warning": "NÃO entregar ao participante.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"{len(selected)} itens ({len(selected) / len(items):.0%}) em {len(chosen_families)} famílias.")


if __name__ == "__main__":
    main()
