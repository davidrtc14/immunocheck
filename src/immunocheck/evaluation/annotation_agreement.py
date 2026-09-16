from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from pathlib import Path

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import EndToEndDatasetError, EndToEndItem


@dataclass(frozen=True, slots=True)
class AnnotationResponse:
    round_id: str
    task_id: str
    item_id: str
    claim: str
    second_label: Verdict
    rationale: str
    sources_consulted: str
    uncertainty: str
    reviewer: str
    reviewed_at: str


def load_annotation_responses(
    path: Path, *, expected_tasks: Mapping[str, EndToEndItem]
) -> tuple[AnnotationResponse, ...]:
    """Lê retornos brutos, inclusive divergências ainda não adjudicadas.

    A existência dos campos não certifica leitura das fontes, identidade ou cegamento.
    Retornos não promovem itens, não sobrescrevem rótulos e não congelam teste.
    """
    try:
        values = [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line
        ]
        responses = []
        fields = tuple(AnnotationResponse.__dataclass_fields__)
        for value in values:
            if not isinstance(value, dict) or value.get("schema_version") != 1:
                raise ValueError("Schema do retorno inválido.")
            if set(value) != {"schema_version", *fields}:
                raise ValueError("Campos inesperados no retorno.")
            if any(not isinstance(value[key], str) or not value[key].strip() for key in fields):
                raise ValueError("Campos incompletos no retorno.")
            data = {key: value[key].strip() for key in fields}
            data["second_label"] = Verdict(data["second_label"])
            response = AnnotationResponse(**data)
            if not re.fullmatch(r"[a-z][a-z0-9_-]{1,63}", response.reviewer):
                raise ValueError("Usar identificador interno, não dados pessoais.")
            if date.fromisoformat(response.reviewed_at).isoformat() != response.reviewed_at:
                raise ValueError("Data deve ser ISO YYYY-MM-DD.")
            original = expected_tasks[response.task_id]
            if original.item_id != response.item_id or original.claim != response.claim:
                raise ValueError("Alegação ou mapeamento diverge do pacote original.")
            if original.reviewer and original.reviewer.casefold() == response.reviewer.casefold():
                raise ValueError("Segundo revisor precisa ser distinto do primeiro.")
            responses.append(response)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise EndToEndDatasetError(
            "Retorno de anotação inválido ou incompatível com o pacote."
        ) from exc
    if not responses:
        raise EndToEndDatasetError("O retorno está vazio.")
    task_ids = [response.task_id for response in responses]
    if len(set(task_ids)) != len(task_ids) or set(task_ids) != set(expected_tasks):
        raise EndToEndDatasetError("O retorno deve cobrir cada tarefa selecionada uma única vez.")
    if len({response.round_id for response in responses}) != 1:
        raise EndToEndDatasetError("Não misturar rodadas no mesmo retorno.")
    if len({response.reviewer for response in responses}) != 1:
        raise EndToEndDatasetError("Não misturar revisores no mesmo retorno.")
    return tuple(sorted(responses, key=lambda response: response.task_id))


def compute_annotation_agreement(
    primary_labels: Mapping[str, Verdict], responses: tuple[AnnotationResponse, ...]
) -> dict[str, object]:
    """Cohen's kappa nominal antes de adjudicação, nunca contra rótulos finais.

    Não interpreta kappa como acurácia do sistema, nem impõe um limiar de aprovação.
    """
    task_ids = [response.task_id for response in responses]
    if not responses or len(set(task_ids)) != len(task_ids) or set(task_ids) != set(primary_labels):
        raise EndToEndDatasetError("Concordância exige pares únicos e completos de rótulos.")
    if any(not isinstance(label, Verdict) for label in primary_labels.values()):
        raise EndToEndDatasetError("Concordância exige rótulos primários originais válidos.")
    total = len(responses)
    primary_counts = Counter(primary_labels.values())
    second_counts = Counter(response.second_label for response in responses)
    disagreements = sorted(
        response.task_id
        for response in responses
        if primary_labels[response.task_id] is not response.second_label
    )
    observed = Fraction(total - len(disagreements), total)
    expected = Fraction(
        sum(primary_counts[label] * second_counts[label] for label in Verdict), total * total
    )
    kappa = (observed - expected) / (1 - expected) if expected != 1 else None
    matrix = {label.value: {second.value: 0 for second in Verdict} for label in Verdict}
    for response in responses:
        matrix[primary_labels[response.task_id].value][response.second_label.value] += 1
    return {
        "total": total,
        "agreement_count": total - len(disagreements),
        "disagreement_count": len(disagreements),
        "disagreement_task_ids": disagreements,
        "observed_agreement": float(observed),
        "expected_agreement": float(expected),
        "cohens_kappa": float(kappa) if kappa is not None else None,
        "primary_counts": {label.value: primary_counts[label] for label in Verdict},
        "second_counts": {label.value: second_counts[label] for label in Verdict},
        "matrix_primary_rows_second_columns": matrix,
        "adjudication_applied": False,
    }
