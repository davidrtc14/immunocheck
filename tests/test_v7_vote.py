from __future__ import annotations

import pytest

from immunocheck.application.proposition_nli import PropositionJudgment, Relation
from immunocheck.application.structured_claim import (
    Proposition,
    PropositionRole,
    PropositionType,
)
from immunocheck.application.v7_vote import ConsistencyVoteJudge, majority
from immunocheck.infrastructure.ollama_seeded import SeededOllamaClient

P1 = Proposition("A vacina é aplicada em duas doses.", PropositionRole.CORE, PropositionType.FACT)
P2 = Proposition("O intervalo é de seis meses.", PropositionRole.PREMISE, PropositionType.FACT)


def _vote(
    proposition: Proposition, relation: Relation, quote: str | None = None
) -> PropositionJudgment:
    return PropositionJudgment(proposition, relation, relation, quote=quote, source_id=quote)


class _Judge:
    def __init__(self, *relations: Relation, tag: str) -> None:
        self.relations, self.tag, self.retries = relations, tag, []

    def judge(self, propositions, evidence, *, retry=False):
        self.retries.append(retry)
        return tuple(
            _vote(prop, relation, f"{self.tag}-{index}")
            for index, (prop, relation) in enumerate(zip(propositions, self.relations, strict=True))
        )


def test_majority_keeps_the_first_matching_judgment() -> None:
    votes = [
        _vote(P1, Relation.CONTRADICTED, "a"),
        _vote(P1, Relation.ENTAILED, "b"),
        _vote(P1, Relation.ENTAILED, "c"),
    ]
    chosen = majority(votes)
    assert chosen.relation is Relation.ENTAILED and chosen.quote == "b"


def test_three_way_split_becomes_not_addressed() -> None:
    votes = [
        _vote(P1, Relation.CONTRADICTED, "a"),
        _vote(P1, Relation.ENTAILED, "b"),
        _vote(P1, Relation.NOT_ADDRESSED),
    ]
    chosen = majority(votes)
    assert chosen.relation is Relation.NOT_ADDRESSED and chosen.quote is None


def test_vote_is_per_proposition_and_forwards_retry() -> None:
    judges = (
        _Judge(Relation.ENTAILED, Relation.CONTRADICTED, tag="j1"),
        _Judge(Relation.ENTAILED, Relation.ENTAILED, tag="j2"),
        _Judge(Relation.NOT_ADDRESSED, Relation.CONTRADICTED, tag="j3"),
    )
    first, second = ConsistencyVoteJudge(judges).judge([P1, P2], [], retry=True)
    assert first.relation is Relation.ENTAILED and first.quote == "j1-0"
    assert second.relation is Relation.CONTRADICTED and second.quote == "j1-1"
    assert all(judge.retries == [True] for judge in judges)


def test_vote_needs_three_judges() -> None:
    with pytest.raises(ValueError):
        ConsistencyVoteJudge((_Judge(tag="a"), _Judge(tag="b")))


def test_seeded_client_sends_its_seed_and_temperature() -> None:
    body = SeededOllamaClient(seed=43, temperature=0.3).payload(
        system_prompt="s", user_prompt="u", schema={"type": "object"}, max_output_tokens=10
    )
    assert body["options"]["seed"] == 43 and body["options"]["temperature"] == 0.3
    with pytest.raises(ValueError):
        SeededOllamaClient(base_url="http://example.org:11434")
