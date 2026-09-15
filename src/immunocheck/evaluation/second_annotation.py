from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from collections.abc import Mapping

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import (
    MINIMUM_DATASET_SIZE,
    DatasetSplit,
    DatasetStatus,
    EndToEndDatasetError,
    EndToEndItem,
)

SECOND_ANNOTATION_SEED = 20260915


def select_second_annotation_items(
    items: tuple[EndToEndItem, ...], *, seed: int = SECOND_ANNOTATION_SEED
) -> tuple[EndToEndItem, ...]:
    """Seleciona 30% por maiores restos, estratificados pelo rótulo primário e split.

    Não consulta o sistema avaliado. A seleção não registra nenhuma anotação.
    """
    if len(items) < MINIMUM_DATASET_SIZE:
        raise EndToEndDatasetError("A seleção exige pelo menos 100 itens com primeira revisão.")
    if len({item.item_id for item in items}) != len(items):
        raise EndToEndDatasetError("A seleção contém IDs duplicados.")
    if any(
        item.status is not DatasetStatus.REVIEWED or item.primary_label is None for item in items
    ):
        raise EndToEndDatasetError("A seleção exige primeira revisão e rótulos originais.")
    if any(item.second_reviewer is not None for item in items):
        raise EndToEndDatasetError(
            "A seleção inicial não deve substituir segundas revisões existentes."
        )
    strata: dict[tuple[str, str], list[EndToEndItem]] = defaultdict(list)
    for item in items:
        assert item.primary_label is not None
        strata[(item.primary_label.value, item.split.value)].append(item)
    expected = {(label.value, split.value) for label in Verdict for split in DatasetSplit}
    if set(strata) != expected:
        raise EndToEndDatasetError("A seleção exige as quatro classes em ambos os splits.")
    # Aritmética inteira evita erro de ponto flutuante no arredondamento de 30%.
    target = (len(items) * 3 + 9) // 10
    quotas = {key: len(values) * 3 // 10 for key, values in strata.items()}
    ranking = sorted(strata, key=lambda key: (-(len(strata[key]) * 3 % 10), key))
    for key in ranking[: target - sum(quotas.values())]:
        quotas[key] += 1
    if any(count == 0 for count in quotas.values()):
        raise EndToEndDatasetError("A amostra de 30% não cobre todos os estratos; rever o plano.")
    rng = random.Random(seed)
    selected: list[EndToEndItem] = []
    for key in sorted(strata):
        selected.extend(rng.sample(sorted(strata[key], key=lambda item: item.item_id), quotas[key]))
    rng.shuffle(selected)
    return tuple(selected)


def render_second_annotation_package(
    items: tuple[EndToEndItem, ...],
    *,
    dataset_text: str,
    corpus_version: str,
    source_catalog: Mapping[str, tuple[str, str]],
    seed: int = SECOND_ANNOTATION_SEED,
) -> dict[str, str]:
    """Produz textos para publicação, separando pacote participante e mapa de auditoria.

    Não escreve arquivos, não usa LLM, não preenche respostas e não congela teste.
    O mapa NÃO deve ser entregue ao participante.
    """
    selected = select_second_annotation_items(items, seed=seed)
    tasks = [
        {
            "task_id": f"annotation-{index:03d}",
            "claim": item.claim,
            "second_label": None,
            "rationale": None,
            "source_urls": [],
            "reviewer_id": None,
            "reviewed_at": None,
        }
        for index, item in enumerate(selected, 1)
    ]
    annotations = "# Formulário de anotação independente\n\n"
    annotations += "Preencher após ler README.md. Campos vazios não contam como revisão.\n\n"
    for task in tasks:
        annotations += (
            f"## {task['task_id']}\n\n{task['claim']}\n\n"
            "- Rótulo:\n- Justificativa:\n- Fontes e trechos/páginas consultados:\n"
            "- Dúvidas ou ambiguidade:\n- Identificador interno do revisor:\n- Data:\n\n"
        )
    readme = """# Instruções ao segundo anotador

Anote individualmente as alegações de ANNOTATIONS.md, sem consultar os rótulos do
primeiro anotador, pareceres do projeto ou respostas do ImmunoCheck. Não use LLM
para substituir seu julgamento. A ordem e os códigos foram embaralhados.
Este é um benchmark acadêmico controlado, com formulações sintéticas; não é uma
amostra de mensagens reais nem um serviço de aconselhamento médico.

Receba somente esta pasta `participant`. O repositório público contém propostas
de resposta: não o consulte durante a anotação. Informe se já viu rótulos ou
justificativas destes itens; a ausência deles neste pacote não prova cegamento.
O primeiro autor não pode ser o segundo anotador.

## Como preencher

1. Leia a proposição inteira, respeitando produto, população, território e data.
   Não complete dados ausentes nem avalie a pessoa que teria publicado o conteúdo.
2. Consulte diretamente o corpus listado em SOURCES.md, incluindo contexto,
   páginas e tabelas pertinentes. Peça ao responsável acesso ao snapshot local
   para documentos indisponíveis na web, respeitando suas licenças. Não use
   evidências posteriores ao recorte temporal para substituir o que era válido nele.
3. Preencha rótulo, justificativa própria, URLs e trechos/páginas em ANNOTATIONS.md.
   Para falta de evidência, descreva a informação ausente e a busca feita. Ausência
   de menção, por si só, não refuta. Não persiga uma distribuição de classes.
4. Registre dúvidas, tempo aproximado total, data e um identificador interno
   sem nome civil, e-mail ou outros dados pessoais. Devolva o formulário ao autor.
   tasks.jsonl é alternativa estruturada opcional; use apenas um dos formulários.
5. As respostas originais serão preservadas. Discordar é permitido: concordância
   será calculada antes de discutir divergências. Não combine respostas com o autor.

## Rótulos

| Rótulo | Critério |
| --- | --- |
| SUPPORTED | A evidência sustenta diretamente a proposição e seu escopo. |
| REFUTED | A evidência contradiz diretamente a proposição central. |
| MISLEADING | Há parte factual relevante sustentada, mas contexto, alcance ou inferência foi distorcido materialmente. Explicitar ambas as partes. |
| INSUFFICIENT_EVIDENCE | Corpus e informação disponível não permitem sustentar nem contradizer com segurança. Não significa verdadeiro ou falso. |

Se não houver parte factual relevante sustentada, não escolher MISLEADING apenas
porque uma afirmação falsa menciona um tema verdadeiro. Marcar ambiguidades para
adjudicação posterior. Fontes conclusivas precisam sustentar o julgamento, não
apenas mencionar vacinação. Não usar normas gerais para provar evento específico.

O catálogo é completo e não ranqueado por alegação; inclui referências, não cópias
dos documentos. A avaliação se refere ao snapshot do corpus, não a uma busca sem
limites na internet. Registrar indisponibilidade e não adivinhar.
"""
    catalog = "# Catálogo não ranqueado do corpus\n\n"
    catalog += f"Snapshot: `{corpus_version}`.\n\n"
    catalog += "Lista completa por identificador de documento, sem associação a tarefas.\n\n"
    for document_id, (title, url) in sorted(source_catalog.items()):
        catalog += f"- {document_id}: [{title.replace('[', '(').replace(']', ')')}]({url})\n"
    normalized = dataset_text.replace("\r\n", "\n").encode("utf-8")
    manifest = {
        "schema_version": 1,
        "purpose": "second_human_annotation_selection",
        "prepared_at": "2026-09-15",
        "test_frozen": False,
        "annotation_completed": False,
        "algorithm": "30% ceiling; primary_label/split strata; largest remainder; Random.sample/shuffle",
        "seed": seed,
        "dataset_sha256": hashlib.sha256(normalized).hexdigest(),
        "corpus_version": corpus_version,
        "total_dataset": len(items),
        "selected": len(selected),
        "share_with_participant": "participant/ only; never this mapping or repository review files",
        "mapping": [
            {
                "task_id": task["task_id"],
                "item_id": item.item_id,
                "primary_label": item.primary_label.value if item.primary_label else None,
                "split": item.split.value,
                "claim_family": item.claim_family,
            }
            for task, item in zip(tasks, selected, strict=True)
        ],
    }
    return {
        "participant/README.md": readme,
        "participant/ANNOTATIONS.md": annotations,
        "participant/SOURCES.md": catalog,
        "participant/tasks.jsonl": "".join(
            json.dumps(task, ensure_ascii=False) + "\n" for task in tasks
        ),
        "selection_manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    }
