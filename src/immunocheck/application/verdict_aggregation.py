"""v5: veredito agregado por regra explícita sobre os julgamentos das proposições (ADR-049)."""

from __future__ import annotations

from collections.abc import Sequence

from immunocheck.application.proposition_nli import PropositionJudgment, Relation
from immunocheck.application.structured_claim import PropositionRole, PropositionType
from immunocheck.domain.models import Verdict

_SUPPORTING_ROLES = frozenset({PropositionRole.CORE, PropositionRole.PREMISE})
_EXTRAPOLATING_TYPES = frozenset(
    {PropositionType.CAUSAL, PropositionType.UNIVERSAL, PropositionType.NORMATIVE}
)


def aggregate_verdict(judgments: Sequence[PropositionJudgment]) -> Verdict:
    """Aplica as regras pré-registradas em `evaluation/refinement_v5/PROTOCOL.md`.

    `ENTAILED` e `CONTRADICTED` só chegam aqui com trecho literal verificado; por isso uma parte
    sustentada usada para `MISLEADING` sempre tem âncora no corpus.
    """

    if not judgments:
        raise ValueError("A agregação exige ao menos um julgamento.")
    relations = [item.relation for item in judgments]
    if len(judgments) == 1:
        return {
            Relation.ENTAILED: Verdict.SUPPORTED,
            Relation.CONTRADICTED: Verdict.REFUTED,
        }.get(relations[0], Verdict.INSUFFICIENT_EVIDENCE)
    if all(relation is Relation.ENTAILED for relation in relations):
        return Verdict.SUPPORTED

    supported = [
        item
        for item in judgments
        if item.relation is Relation.ENTAILED and item.proposition.role in _SUPPORTING_ROLES
    ]
    if supported:
        for item in judgments:
            role, kind = item.proposition.role, item.proposition.type
            if role is PropositionRole.CONCLUSION and item.relation is Relation.CONTRADICTED:
                return Verdict.MISLEADING
            if (
                role is PropositionRole.CONCLUSION
                and item.relation is Relation.NOT_ADDRESSED
                and kind in _EXTRAPOLATING_TYPES
            ):
                return Verdict.MISLEADING
            if role in _SUPPORTING_ROLES and item.relation is Relation.CONTRADICTED:
                return Verdict.MISLEADING
    if Relation.CONTRADICTED in relations and Relation.ENTAILED not in relations:
        return Verdict.REFUTED
    return Verdict.INSUFFICIENT_EVIDENCE
