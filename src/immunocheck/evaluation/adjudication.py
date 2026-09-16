"""Importação auditável de decisões humanas; não julga evidências nem congela teste."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.annotation_agreement import AnnotationResponse
from immunocheck.evaluation.end_to_end import (
    EndToEndDatasetError,
    EndToEndItem,
    validate_dataset_ready,
    validate_end_to_end_items,
)

FIELDS = (
    "Rótulo final proposto (ou PENDENTE)",
    "Fundamentação e aplicação do manual",
    "Fontes, trechos/páginas e chunks conferidos",
    "Ação sobre o item (manter, corrigir, excluir ou pendente)",
    "Correção textual sugerida, se necessária",
    "Identificador interno do responsável",
    "Data",
)
DECISION_MARKERS = ("### Decisão humana a preencher", "### Decisão a preencher")
CHUNK_PATTERN = re.compile(r"(?<![\w:-])[a-zA-Z0-9_-]+:p\d+:c\d+:[a-f0-9]{12}(?![\w:-])")
CONFIRMED_CHUNKS_PATTERN = re.compile(
    r"\bchunks? conferidos?(?: em [^:.;\n]+)?(?::|\s)([^.\n]+)", re.IGNORECASE
)
REVIEWER_PATTERN = re.compile(r"[a-z][a-z0-9_-]{1,63}")


@dataclass(frozen=True, slots=True)
class AdjudicationDecision:
    task_id: str
    item_id: str
    final_label: Verdict | None
    rationale: str | None
    sources_checked: str | None
    evidence_chunk_ids: tuple[str, ...]
    action: str
    claim_correction: str | None
    reviewer: str | None
    reviewed_at: str | None


@dataclass(frozen=True, slots=True)
class AdjudicationCandidate:
    items: tuple[EndToEndItem, ...]
    excluded_item_ids: tuple[str, ...]
    applied_task_ids: tuple[str, ...]
    decisions: tuple[AdjudicationDecision, ...]
    structurally_ready: bool
    readiness_error: str | None
    test_frozen: bool = False


def load_adjudication_decisions(
    path: Path,
    *,
    expected_tasks: Mapping[str, str],
    expected_claims: Mapping[str, str] | None = None,
) -> tuple[AdjudicationDecision, ...]:
    """Aceita cópia preenchida de TASKS.md ou template JSONL; preserva os originais."""
    try:
        text = path.read_text("utf-8-sig")
        if path.suffix.lower() == ".md":
            values = _markdown_values(text, expected_claims=expected_claims)
        elif path.suffix.lower() == ".jsonl":
            values = [json.loads(line) for line in text.splitlines() if line.strip()]
        else:
            raise ValueError("Use Markdown ou JSONL.")
        decisions = tuple(_parse_decision(value) for value in values)
        ids = [decision.task_id for decision in decisions]
        if len(set(ids)) != len(ids) or set(ids) != set(expected_tasks):
            raise ValueError("Decisões não correspondem ao pacote completo esperado.")
        if any(expected_tasks[d.task_id] != d.item_id for d in decisions):
            raise ValueError("Mapeamento de alegação alterado.")
        return decisions
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise EndToEndDatasetError("Formulário de adjudicação inválido.") from exc


def pending_decision_ids(decisions: tuple[AdjudicationDecision, ...]) -> tuple[str, ...]:
    return tuple(d.task_id for d in decisions if not _is_complete(d))


def assemble_adjudication_candidate(
    items: tuple[EndToEndItem, ...],
    responses: tuple[AnnotationResponse, ...],
    decisions: tuple[AdjudicationDecision, ...],
    *,
    expected_tasks: Mapping[str, str],
    valid_chunk_ids: AbstractSet[str],
) -> AdjudicationCandidate:
    """Monta apenas candidato em memória; decisão humana é dado, nunca instrução."""
    items = validate_end_to_end_items(items, valid_chunk_ids=valid_chunk_ids, require_reviewed=True)
    if any(item.second_reviewer or item.adjudicator for item in items):
        raise EndToEndDatasetError(
            "A incorporação exige o snapshot primário, sem revisão aplicada."
        )
    by_id = {item.item_id: item for item in items}
    by_task = {r.task_id: r for r in responses}
    if len(by_task) != len(responses) or len({r.item_id for r in responses}) != len(responses):
        raise EndToEndDatasetError("Retornos duplicados.")
    if not responses or len({r.round_id for r in responses}) != 1:
        raise EndToEndDatasetError("Use uma única rodada completa de retornos.")
    if len({r.reviewer for r in responses}) != 1:
        raise EndToEndDatasetError("O pacote exige um segundo anotador distinto.")
    for response in responses:
        item = by_id.get(response.item_id)
        if item is None or item.claim != response.claim or item.primary_label is None:
            raise EndToEndDatasetError("Retorno não corresponde ao snapshot primário.")
        if not REVIEWER_PATTERN.fullmatch(response.reviewer):
            raise EndToEndDatasetError("Identificador de revisor inválido.")
        if response.reviewer.casefold() == item.reviewer.casefold():
            raise EndToEndDatasetError("O segundo anotador deve ser distinto do primeiro.")
        try:
            if date.fromisoformat(response.reviewed_at).isoformat() != response.reviewed_at:
                raise ValueError
        except ValueError as exc:
            raise EndToEndDatasetError("Data do retorno inválida.") from exc
        if not isinstance(response.second_label, Verdict):
            raise EndToEndDatasetError("Rótulo do retorno inválido.")
    if set(expected_tasks) - set(by_task):
        raise EndToEndDatasetError("Tarefa de adjudicação sem segundo retorno.")
    if any(by_task[task].item_id != item_id for task, item_id in expected_tasks.items()):
        raise EndToEndDatasetError("Mapeamento de adjudicação alterado.")
    by_decision = {d.task_id: d for d in decisions}
    if len(by_decision) != len(decisions) or set(by_decision) != set(expected_tasks):
        raise EndToEndDatasetError("Decisões não cobrem exatamente o pacote esperado.")
    for decision in decisions:
        # Revalida dataclasses criadas diretamente, não apenas arquivos importados.
        _validate_decision(decision)
        if decision.item_id != expected_tasks[decision.task_id]:
            raise EndToEndDatasetError("Decisão aponta para outro item.")
    pending = pending_decision_ids(decisions)
    if pending:
        raise EndToEndDatasetError("Decisões humanas pendentes: " + ", ".join(pending))
    corrections = [d.task_id for d in decisions if d.claim_correction and d.action != "excluir"]
    if corrections:
        raise EndToEndDatasetError(
            "Correção textual exige nova anotação antes da incorporação: " + ", ".join(corrections)
        )
    candidate = dict(by_id)
    excluded: list[str] = []
    for response in responses:
        item = by_id[response.item_id]
        decision = by_decision.get(response.task_id)
        if decision and decision.action == "excluir":
            del candidate[item.item_id]
            excluded.append(item.item_id)
            continue
        disagreement = response.second_label is not item.primary_label
        if disagreement and decision is None:
            raise EndToEndDatasetError("Divergência sem decisão humana: " + response.task_id)
        updated = replace(
            item,
            second_reviewer=response.reviewer,
            second_label=response.second_label,
            second_reviewed_at=response.reviewed_at,
        )
        if decision:
            unknown = set(decision.evidence_chunk_ids) - valid_chunk_ids
            if unknown:
                raise EndToEndDatasetError("Decisão referencia chunks ausentes do corpus.")
            updated = replace(
                updated,
                label=decision.final_label,
                rationale=decision.rationale,
                evidence_chunk_ids=decision.evidence_chunk_ids,
                adjudicator=decision.reviewer,
                adjudicated_at=decision.reviewed_at,
                adjudication_basis="annotation_disagreement" if disagreement else "evidence_audit",
                # Justificativa primária continua preservada no snapshot e nas rodadas arquivadas.
            )
        candidate[item.item_id] = updated
    validated = validate_end_to_end_items(
        tuple(candidate.values()), valid_chunk_ids=valid_chunk_ids, require_reviewed=True
    )
    error = None
    try:
        validate_dataset_ready(validated)
    except EndToEndDatasetError as exc:
        error = str(exc)
    return AdjudicationCandidate(
        items=validated,
        excluded_item_ids=tuple(excluded),
        applied_task_ids=tuple(by_decision),
        decisions=decisions,
        structurally_ready=error is None,
        readiness_error=error,
    )


def _is_complete(decision: AdjudicationDecision) -> bool:
    if decision.action == "pendente":
        return False
    common = bool(decision.rationale and decision.reviewer and decision.reviewed_at)
    if decision.action == "excluir":
        return common
    return common and bool(
        decision.final_label
        and decision.sources_checked
        and (decision.final_label is Verdict.INSUFFICIENT_EVIDENCE or decision.evidence_chunk_ids)
    )


def _validate_decision(decision: AdjudicationDecision) -> None:
    if decision.final_label is not None and not isinstance(decision.final_label, Verdict):
        raise EndToEndDatasetError("Rótulo inválido na decisão humana.")
    if not decision.task_id or not decision.item_id:
        raise EndToEndDatasetError("Identificação da tarefa ausente.")
    if any(
        not isinstance(chunk, str) or not chunk.strip() for chunk in decision.evidence_chunk_ids
    ):
        raise EndToEndDatasetError("Lista de chunks inválida.")
    if decision.action not in {"manter", "corrigir", "excluir", "pendente"}:
        raise EndToEndDatasetError("Ação inválida na decisão humana.")
    if decision.reviewer and not REVIEWER_PATTERN.fullmatch(decision.reviewer):
        raise EndToEndDatasetError("Use código interno, sem nome ou vínculo institucional.")
    if decision.reviewed_at:
        try:
            valid_date = date.fromisoformat(decision.reviewed_at)
        except ValueError as exc:
            raise EndToEndDatasetError("Data da decisão inválida.") from exc
        if valid_date.isoformat() != decision.reviewed_at:
            raise EndToEndDatasetError("Use data ISO na decisão.")
    if len(set(decision.evidence_chunk_ids)) != len(decision.evidence_chunk_ids):
        raise EndToEndDatasetError("Chunk duplicado na decisão.")
    if decision.final_label is Verdict.INSUFFICIENT_EVIDENCE and decision.evidence_chunk_ids:
        raise EndToEndDatasetError("Abstenção deve ter lista vazia de evidências conclusivas.")


def _parse_decision(value: object) -> AdjudicationDecision:
    keys = {
        "schema_version",
        "task_id",
        "item_id",
        "final_label",
        "rationale",
        "sources_checked",
        "evidence_chunk_ids",
        "action",
        "claim_correction",
        "reviewer",
        "reviewed_at",
    }
    if not isinstance(value, dict) or set(value) != keys or value["schema_version"] != 1:
        raise ValueError("Campos ou versão inválidos.")
    chunks = value["evidence_chunk_ids"]
    if not isinstance(chunks, list) or any(not isinstance(c, str) or not c.strip() for c in chunks):
        raise ValueError("Lista de chunks inválida.")
    label_text = _text(value["final_label"])
    decision = AdjudicationDecision(
        task_id=_text(value["task_id"]) or "",
        item_id=_text(value["item_id"]) or "",
        final_label=None if label_text in (None, "PENDENTE") else Verdict(label_text),
        rationale=_text(value["rationale"]),
        sources_checked=_text(value["sources_checked"]),
        evidence_chunk_ids=tuple(c.strip() for c in chunks),
        action=(_text(value["action"]) or "pendente").casefold(),
        claim_correction=_claim_correction(value["claim_correction"]),
        reviewer=_text(value["reviewer"]),
        reviewed_at=_text(value["reviewed_at"]),
    )
    _validate_decision(decision)
    return decision


def _text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("Campo textual inválido.")
    return value.strip() or None


def _claim_correction(value: object) -> str | None:
    text = _text(value)
    if text and re.match(r"^nenhuma\b", text, re.IGNORECASE):
        return None
    return text


def _confirmed_chunk_ids(sources: str) -> list[str]:
    return list(
        dict.fromkeys(
            chunk_id
            for match in CONFIRMED_CHUNKS_PATTERN.finditer(sources)
            for chunk_id in CHUNK_PATTERN.findall(match.group(1))
        )
    )


def _markdown_values(
    text: str, *, expected_claims: Mapping[str, str] | None = None
) -> list[dict[str, object]]:
    sections = re.split(r"(?m)^## (annotation-\d{3}) — (e2e-\d{4})\s*$", text)
    values = []
    for index in range(1, len(sections), 3):
        task_id, item_id, body = sections[index : index + 3]
        if expected_claims is not None:
            claim = body.strip().split("\n\n", 1)[0].strip()
            if task_id not in expected_claims or claim != expected_claims[task_id]:
                raise ValueError(
                    "Alegação alterada no formulário; registrar correção separadamente."
                )
        markers = [marker for marker in DECISION_MARKERS if body.count(marker)]
        if len(markers) != 1 or body.count(markers[0]) != 1:
            raise ValueError("Seção de decisão ausente ou duplicada.")
        content = body.split(markers[0])[1]
        fields: dict[str, str] = {}
        active = None
        for line in content.splitlines():
            match = re.match(r"^- ([^:]+):(.*)$", line)
            if match:
                active, answer = match.groups()
                if active not in FIELDS or active in fields:
                    raise ValueError("Campo desconhecido ou duplicado.")
                fields[active] = answer.strip()
            elif line.strip():
                if active is None or line.startswith("#"):
                    raise ValueError("Formato da decisão inválido.")
                fields[active] += "\n" + line.strip()
        if set(fields) != set(FIELDS):
            raise ValueError("Campos ausentes na decisão.")
        reviewed_at = fields[FIELDS[6]]
        if re.fullmatch(r"\d{2}/\d{2}/\d{4}", reviewed_at):
            day, month, year = map(int, reviewed_at.split("/"))
            reviewed_at = date(year, month, day).isoformat()
        values.append(
            {
                "schema_version": 1,
                "task_id": task_id,
                "item_id": item_id,
                "final_label": fields[FIELDS[0]],
                "rationale": fields[FIELDS[1]],
                "sources_checked": fields[FIELDS[2]],
                "evidence_chunk_ids": _confirmed_chunk_ids(fields[FIELDS[2]]),
                "action": fields[FIELDS[3]],
                "claim_correction": fields[FIELDS[4]],
                "reviewer": fields[FIELDS[5]],
                "reviewed_at": reviewed_at,
            }
        )
    return values
