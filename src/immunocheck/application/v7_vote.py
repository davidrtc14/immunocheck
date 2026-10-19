"""v7 (ADR-054), candidata C5: voto por consistência no juiz.

Três juízes iguais, com temperatura 0,3 e sementes diferentes, julgam as mesmas proposições. Cada
proposição fica com a relação que tiver pelo menos dois votos, usando o julgamento (trecho e fonte)
do primeiro juiz que votou nela; sem maioria, vira `NOT_ADDRESSED`.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from immunocheck.application.proposition_nli import PropositionJudgment, Relation
from immunocheck.application.structured_claim import Proposition
from immunocheck.domain.models import Evidence

MIN_VOTES = 2


class Judge(Protocol):
    def judge(
        self,
        propositions: Sequence[Proposition],
        evidence: Sequence[Evidence],
        *,
        retry: bool = False,
    ) -> tuple[PropositionJudgment, ...]: ...


def majority(votes: Sequence[PropositionJudgment]) -> PropositionJudgment:
    counts = Counter(vote.relation for vote in votes)
    relation, count = counts.most_common(1)[0]
    if count < MIN_VOTES:
        return PropositionJudgment(
            votes[0].proposition, Relation.NOT_ADDRESSED, Relation.NOT_ADDRESSED
        )
    return next(vote for vote in votes if vote.relation is relation)


@dataclass(frozen=True, slots=True)
class ConsistencyVoteJudge:
    judges: tuple[Judge, ...]

    def __post_init__(self) -> None:
        if len(self.judges) < MIN_VOTES + 1:
            raise ValueError("O voto por consistência exige pelo menos três juízes.")

    def judge(
        self,
        propositions: Sequence[Proposition],
        evidence: Sequence[Evidence],
        *,
        retry: bool = False,
    ) -> tuple[PropositionJudgment, ...]:
        ballots = [item.judge(propositions, evidence, retry=retry) for item in self.judges]
        return tuple(majority(votes) for votes in zip(*ballots, strict=True))
