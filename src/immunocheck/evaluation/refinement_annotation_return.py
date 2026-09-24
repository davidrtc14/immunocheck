from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from fractions import Fraction

from immunocheck.domain.models import Verdict
from immunocheck.evaluation.end_to_end import EndToEndItem

HUMAN_ATTESTATIONS = (
    "Sou uma pessoa e realizei esta anotação por julgamento próprio.",
    "Sou diferente do primeiro revisor e não consultei seus rótulos.",
    "Não usei LLM ou outro sistema automático para substituir meu julgamento.",
)


@dataclass(frozen=True, slots=True)
class RefinementAnnotationResponse:
    task_id: str
    claim: str
    second_label: Verdict
    rationale: str
    sources_consulted: str
    uncertainty: str


@dataclass(frozen=True, slots=True)
class RefinementReturnInspection:
    reviewer: str | None
    reviewed_at: str | None
    responses: tuple[RefinementAnnotationResponse, ...]
    rejection_reasons: tuple[str, ...]
    agreement: dict[str, object] | None

    @property
    def eligible_for_human_gate(self) -> bool:
        return not self.rejection_reasons


def inspect_refinement_annotation_return(
    text: str,
    *,
    expected_tasks: Mapping[str, EndToEndItem],
) -> RefinementReturnInspection:
    """Inspeciona o formulário sem promover rótulos nem certificar identidade humana."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    reasons: list[str] = []
    if not all(
        re.search(
            rf"(?mi)^- \[\s*x\s*\]\s+{re.escape(statement)}\s*$",
            normalized,
        )
        for statement in HUMAN_ATTESTATIONS
    ):
        reasons.append("missing_human_attestation")
    if re.search(r"não é anotação humana|\bia[- ]assistente\b", normalized, re.IGNORECASE):
        reasons.append("explicit_nonhuman_reviewer")

    reviewer = _header_field(normalized, "Código interno do revisor")
    reviewed_at = _header_field(normalized, "Data da revisão")
    sections = re.split(r"(?m)^## (ref2-annotation-\d{3})\s*$", normalized)
    responses: list[RefinementAnnotationResponse] = []
    section_reviewers: set[str] = set()
    section_dates: set[str] = set()
    for index in range(1, len(sections), 2):
        task_id = sections[index]
        body = sections[index + 1].strip()
        try:
            claim, fields = _parse_task_body(body)
            response = RefinementAnnotationResponse(
                task_id=task_id,
                claim=claim,
                second_label=Verdict(fields["Rótulo"]),
                rationale=fields["Justificativa"],
                sources_consulted=fields["Fontes e trechos/páginas consultados"],
                uncertainty=fields["Dúvidas ou ambiguidade"],
            )
            responses.append(response)
            if value := fields.get("Código interno do revisor"):
                section_reviewers.add(value)
            if value := fields.get("Data"):
                section_dates.add(value)
        except (KeyError, ValueError):
            reasons.append(f"invalid_or_incomplete_task:{task_id}")

    if reviewer is None and len(section_reviewers) == 1:
        reviewer = next(iter(section_reviewers))
    if reviewed_at is None and len(section_dates) == 1:
        reviewed_at = next(iter(section_dates))
    if not reviewer:
        reasons.append("missing_reviewer_code")
    elif not re.fullmatch(r"[a-z][a-z0-9_-]{1,63}", reviewer):
        reasons.append("invalid_reviewer_code")
    if not reviewed_at:
        reasons.append("missing_review_date")
    else:
        try:
            reviewed_at = _normalize_date(reviewed_at)
        except ValueError:
            reasons.append("invalid_review_date")

    task_ids = [response.task_id for response in responses]
    if len(task_ids) != len(set(task_ids)) or set(task_ids) != set(expected_tasks):
        reasons.append("incomplete_or_duplicate_task_set")
    for response in responses:
        expected = expected_tasks.get(response.task_id)
        if expected is not None and response.claim != expected.claim:
            reasons.append(f"changed_claim:{response.task_id}")
        if (
            expected is not None
            and expected.reviewer
            and reviewer
            and expected.reviewer.casefold() == reviewer.casefold()
        ):
            reasons.append("same_as_primary_reviewer")

    agreement = _agreement(responses, expected_tasks) if not _mapping_errors(reasons) else None
    if agreement is not None:
        agreement["valid_for_interhuman_agreement"] = not reasons
    return RefinementReturnInspection(
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        responses=tuple(sorted(responses, key=lambda response: response.task_id)),
        rejection_reasons=tuple(dict.fromkeys(reasons)),
        agreement=agreement,
    )


def _parse_task_body(body: str) -> tuple[str, dict[str, str]]:
    marker = "\n- Rótulo:"
    if marker not in body:
        raise ValueError("Rótulo ausente.")
    claim, raw_fields = body.split(marker, 1)
    fields: dict[str, str] = {"Rótulo": raw_fields.splitlines()[0].strip()}
    for line in raw_fields.splitlines()[1:]:
        match = re.fullmatch(r"- ([^:]+):\s*(.*)", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    required = (
        "Rótulo",
        "Justificativa",
        "Fontes e trechos/páginas consultados",
        "Dúvidas ou ambiguidade",
    )
    if not claim.strip() or any(not fields.get(field) for field in required):
        raise ValueError("Tarefa incompleta.")
    return claim.strip(), fields


def _header_field(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(label)}:\s*(.+)$", text)
    return match.group(1).strip() if match else None


def _mapping_errors(reasons: list[str]) -> bool:
    return "incomplete_or_duplicate_task_set" in reasons


def _normalize_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        day, month, year = value.split("/")
        return date(int(year), int(month), int(day)).isoformat()


def _agreement(
    responses: list[RefinementAnnotationResponse],
    expected_tasks: Mapping[str, EndToEndItem],
) -> dict[str, object]:
    total = len(responses)
    primary = {task_id: item.primary_label for task_id, item in expected_tasks.items()}
    disagreements = [
        response.task_id
        for response in responses
        if primary[response.task_id] is not response.second_label
    ]
    primary_counts = Counter(primary.values())
    second_counts = Counter(response.second_label for response in responses)
    observed = Fraction(total - len(disagreements), total)
    expected = Fraction(
        sum(primary_counts[label] * second_counts[label] for label in Verdict),
        total * total,
    )
    kappa = (observed - expected) / (1 - expected) if expected != 1 else None
    return {
        "total": total,
        "agreement_count": total - len(disagreements),
        "disagreement_count": len(disagreements),
        "disagreement_task_ids": sorted(disagreements),
        "observed_agreement": float(observed),
        "cohens_kappa": float(kappa) if kappa is not None else None,
    }
