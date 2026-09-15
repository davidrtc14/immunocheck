from __future__ import annotations

import json
from collections import Counter
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from immunocheck.domain.models import Verdict

END_TO_END_SCHEMA_VERSION = 1
MINIMUM_DATASET_SIZE = 100
TARGET_DATASET_SIZE = 160
MINIMUM_SECOND_REVIEW_FRACTION = 0.30
MINIMUM_ITEMS_PER_CLASS = 25


class EndToEndDatasetError(RuntimeError):
    """Indica que o dataset fim a fim não é auditável ou ainda não está pronto."""


class DatasetSplit(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"


class DatasetStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"


@dataclass(frozen=True, slots=True)
class EndToEndItem:
    item_id: str
    claim: str
    label: Verdict
    topic: str
    split: DatasetSplit
    status: DatasetStatus
    atomic: bool
    evidence_chunk_ids: tuple[str, ...]
    rationale: str | None
    origin_type: str
    origin_reference: str | None
    reviewer: str | None
    reviewed_at: str | None
    second_reviewer: str | None
    second_label: Verdict | None
    second_reviewed_at: str | None
    adjudicator: str | None
    adjudicated_at: str | None
    notes: str | None
    claim_family: str | None = None
    primary_label: Verdict | None = None


@dataclass(frozen=True, slots=True)
class EndToEndDatasetSummary:
    total: int
    reviewed: int
    second_reviewed: int
    second_review_fraction: float
    labels: dict[str, int]
    splits: dict[str, int]
    topics: dict[str, int]


def load_end_to_end_items(
    path: Path,
    *,
    valid_chunk_ids: AbstractSet[str] | None = None,
    require_reviewed: bool = False,
) -> tuple[EndToEndItem, ...]:
    if not path.is_file():
        raise EndToEndDatasetError(f"Dataset ausente: {path}")

    items: list[EndToEndItem] = []
    try:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if line.strip():
                    items.append(_parse_item(json.loads(line), line_number))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError("O dataset fim a fim está inválido.") from exc

    if not items:
        raise EndToEndDatasetError("O dataset fim a fim está vazio.")
    item_ids = [item.item_id for item in items]
    if len(item_ids) != len(set(item_ids)):
        raise EndToEndDatasetError("O dataset contém item_id duplicado.")
    normalized_claims = [" ".join(item.claim.casefold().split()) for item in items]
    if len(normalized_claims) != len(set(normalized_claims)):
        raise EndToEndDatasetError("O dataset contém alegações duplicadas.")

    family_splits: dict[str, set[DatasetSplit]] = {}
    for item in items:
        if item.claim_family:
            family_splits.setdefault(item.claim_family, set()).add(item.split)
    if any(len(splits) > 1 for splits in family_splits.values()):
        raise EndToEndDatasetError("Uma família de alegações aparece em desenvolvimento e teste.")

    if require_reviewed:
        drafts = [item.item_id for item in items if item.status is DatasetStatus.DRAFT]
        if drafts:
            raise EndToEndDatasetError("Existem itens sem revisão humana: " + ", ".join(drafts))
    if valid_chunk_ids is not None:
        unknown = sorted(
            chunk_id
            for item in items
            for chunk_id in item.evidence_chunk_ids
            if chunk_id not in valid_chunk_ids
        )
        if unknown:
            raise EndToEndDatasetError(
                "O dataset referencia chunks ausentes do corpus: " + ", ".join(unknown)
            )
    return tuple(items)


def summarize_end_to_end_items(items: tuple[EndToEndItem, ...]) -> EndToEndDatasetSummary:
    if not items:
        raise EndToEndDatasetError("O resumo exige pelo menos um item.")
    reviewed = tuple(item for item in items if item.status is DatasetStatus.REVIEWED)
    second_reviewed = sum(item.second_reviewer is not None for item in reviewed)
    return EndToEndDatasetSummary(
        total=len(items),
        reviewed=len(reviewed),
        second_reviewed=second_reviewed,
        second_review_fraction=second_reviewed / len(reviewed) if reviewed else 0.0,
        labels=dict(sorted(Counter(item.label.value for item in items).items())),
        splits=dict(sorted(Counter(item.split.value for item in items).items())),
        topics=dict(sorted(Counter(item.topic for item in items).items())),
    )


def validate_dataset_ready(items: tuple[EndToEndItem, ...]) -> EndToEndDatasetSummary:
    summary = summarize_end_to_end_items(items)
    if summary.total < MINIMUM_DATASET_SIZE:
        raise EndToEndDatasetError(
            f"O dataset possui {summary.total} itens; o mínimo documentado é {MINIMUM_DATASET_SIZE}."
        )
    if summary.reviewed != summary.total:
        raise EndToEndDatasetError("Todos os itens precisam de revisão humana antes da avaliação.")
    if summary.second_review_fraction < MINIMUM_SECOND_REVIEW_FRACTION:
        raise EndToEndDatasetError("A segunda revisão cobre menos de 30% do dataset.")
    expected_labels = {verdict.value for verdict in Verdict}
    if set(summary.labels) != expected_labels:
        raise EndToEndDatasetError("O dataset pronto precisa representar as quatro classes.")
    if set(summary.splits) != {split.value for split in DatasetSplit}:
        raise EndToEndDatasetError("O dataset pronto precisa conter desenvolvimento e teste.")
    if any(count < MINIMUM_ITEMS_PER_CLASS for count in summary.labels.values()):
        raise EndToEndDatasetError("Cada classe precisa de pelo menos 25 itens.")
    if any(not item.claim_family for item in items):
        raise EndToEndDatasetError("Todos os itens precisam de uma família de alegações.")
    if any(item.primary_label is None for item in items):
        raise EndToEndDatasetError(
            "Todos os itens precisam preservar o rótulo do primeiro anotador."
        )
    for verdict in Verdict:
        selected = tuple(item for item in items if item.label is verdict)
        expected_development = round(len(selected) * 0.60)
        actual_development = sum(item.split is DatasetSplit.DEVELOPMENT for item in selected)
        if actual_development != expected_development:
            raise EndToEndDatasetError("O split deve ser estratificado em 60%/40% por classe.")
    return summary


def _parse_item(value: object, line_number: int) -> EndToEndItem:
    if not isinstance(value, dict):
        raise TypeError(f"A linha {line_number} deve conter um objeto JSON.")
    if value.get("schema_version") != END_TO_END_SCHEMA_VERSION:
        raise ValueError(f"Versão de schema inválida na linha {line_number}.")

    item_id = _required_text(value, "item_id", line_number)
    claim = _required_text(value, "claim", line_number)
    if len(claim) > 600:
        raise ValueError(f"Alegação excessivamente longa na linha {line_number}.")
    label = Verdict(_required_text(value, "label", line_number))
    topic = _required_text(value, "topic", line_number)
    split = DatasetSplit(_required_text(value, "split", line_number))
    status = DatasetStatus(_required_text(value, "status", line_number))
    atomic = value.get("atomic")
    if not isinstance(atomic, bool):
        raise TypeError(f"Campo atomic inválido na linha {line_number}.")

    evidence_chunk_ids = _text_list(value, "evidence_chunk_ids", line_number)
    if len(set(evidence_chunk_ids)) != len(evidence_chunk_ids):
        raise ValueError(f"Chunk de evidência duplicado na linha {line_number}.")
    if label is Verdict.INSUFFICIENT_EVIDENCE and evidence_chunk_ids:
        raise ValueError(f"Abstenção não pode ter evidência conclusiva na linha {line_number}.")

    rationale = _optional_text(value, "rationale", line_number)
    origin_type = _required_text(value, "origin_type", line_number)
    origin_reference = _optional_text(value, "origin_reference", line_number)
    reviewer = _optional_text(value, "reviewer", line_number)
    reviewed_at = _optional_text(value, "reviewed_at", line_number)
    second_reviewer = _optional_text(value, "second_reviewer", line_number)
    second_label_text = _optional_text(value, "second_label", line_number)
    second_label = Verdict(second_label_text) if second_label_text else None
    second_reviewed_at = _optional_text(value, "second_reviewed_at", line_number)
    adjudicator = _optional_text(value, "adjudicator", line_number)
    adjudicated_at = _optional_text(value, "adjudicated_at", line_number)
    notes = _optional_text(value, "notes", line_number)
    claim_family = _optional_text(value, "claim_family", line_number)
    primary_label_text = _optional_text(value, "primary_label", line_number)
    primary_label = Verdict(primary_label_text) if primary_label_text else None

    if status is DatasetStatus.DRAFT and any(
        (
            reviewer,
            reviewed_at,
            rationale,
            primary_label,
            second_reviewer,
            second_label,
            second_reviewed_at,
            adjudicator,
            adjudicated_at,
        )
    ):
        raise ValueError(f"Rascunho declara revisão na linha {line_number}.")
    if status is DatasetStatus.REVIEWED:
        if not atomic or not rationale or not reviewer or not reviewed_at:
            raise ValueError(f"Item revisado está incompleto na linha {line_number}.")
        if label is not Verdict.INSUFFICIENT_EVIDENCE and not evidence_chunk_ids:
            raise ValueError(f"Veredito conclusivo sem evidência na linha {line_number}.")

    second_fields = (second_reviewer, second_label, second_reviewed_at)
    if any(second_fields) and not all(second_fields):
        raise ValueError(f"Segunda revisão incompleta na linha {line_number}.")
    if reviewer and second_reviewer and reviewer.casefold() == second_reviewer.casefold():
        raise ValueError(f"A segunda revisão deve ser independente na linha {line_number}.")
    original_label = primary_label if primary_label is not None else label
    disagreement = second_label is not None and second_label is not original_label
    if disagreement and not (adjudicator and adjudicated_at):
        raise ValueError(f"Divergência sem adjudicação na linha {line_number}.")
    if not disagreement and (adjudicator or adjudicated_at):
        raise ValueError(f"Adjudicação sem divergência na linha {line_number}.")
    if not disagreement and label is not original_label:
        raise ValueError(f"Rótulo final alterado sem adjudicação na linha {line_number}.")

    return EndToEndItem(
        item_id=item_id,
        claim=claim,
        label=label,
        topic=topic,
        split=split,
        status=status,
        atomic=atomic,
        evidence_chunk_ids=evidence_chunk_ids,
        rationale=rationale,
        origin_type=origin_type,
        origin_reference=origin_reference,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        second_reviewer=second_reviewer,
        second_label=second_label,
        second_reviewed_at=second_reviewed_at,
        adjudicator=adjudicator,
        adjudicated_at=adjudicated_at,
        notes=notes,
        claim_family=claim_family,
        primary_label=primary_label,
    )


def _required_text(value: dict[str, object], field: str, line_number: int) -> str:
    text = value.get(field)
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    return text.strip()


def _optional_text(value: dict[str, object], field: str, line_number: int) -> str | None:
    text = value.get(field)
    if text is None:
        return None
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    return text.strip()


def _text_list(value: dict[str, object], field: str, line_number: int) -> tuple[str, ...]:
    items = value.get(field)
    if not isinstance(items, list) or any(
        not isinstance(item, str) or not item.strip() for item in items
    ):
        raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    return tuple(item.strip() for item in items)
