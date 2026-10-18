from __future__ import annotations

from typing import Any

import pytest

from immunocheck.application.proposition_nli import DowngradeReason, PropositionJudgment, Relation
from immunocheck.application.structured_claim import (
    Proposition,
    PropositionRole,
    PropositionType,
)
from immunocheck.application.text_components import ModelOutputError
from immunocheck.application.v7_verdict import (
    FRAMING_SYSTEM_PROMPT,
    FramedJudgment,
    FramingPropositionJudge,
    aggregate_verdict_v7,
    framed_post_rules,
)
from immunocheck.domain.models import Evidence, Verdict

CORE = Proposition(
    "A vacina contra gripe é segura para qualquer pessoa com alergia ao ovo.",
    PropositionRole.CORE,
    PropositionType.UNIVERSAL,
)
CHUNK = Evidence(
    chunk_id="doc:p1:c1",
    text="Pessoas com alergia ao ovo podem receber a vacina influenza, com observação por 30 "
    "minutos nos casos de reação grave prévia.",
    source_name="MS",
    document_title="Manual",
    url="https://example.org",
)
ALIASES = {"E1": CHUNK}
QUOTE = "Pessoas com alergia ao ovo podem receber a vacina influenza"


def _raw(relation: str, quote: str | None = QUOTE, ref: str | None = "E1") -> dict[str, Any]:
    return {"proposition": "P1", "relation": relation, "source_ref": ref, "quote": quote}


def test_partial_with_verified_quote_becomes_misleading() -> None:
    judgment = framed_post_rules(CORE, _raw("PARTIAL"), ALIASES)
    assert judgment.partial and judgment.relation is Relation.ENTAILED
    assert judgment.source_id == "doc:p1:c1"
    assert aggregate_verdict_v7([judgment]) is Verdict.MISLEADING


def test_partial_without_verified_quote_is_downgraded() -> None:
    judgment = framed_post_rules(
        CORE, _raw("PARTIAL", quote="frase que não está no trecho"), ALIASES
    )
    assert not judgment.partial and judgment.relation is Relation.NOT_ADDRESSED
    assert judgment.downgrade_reason is DowngradeReason.NO_VERIFIED_QUOTE
    assert aggregate_verdict_v7([judgment]) is Verdict.INSUFFICIENT_EVIDENCE


def test_partial_skips_the_number_rule_but_entailed_does_not() -> None:
    numeric = Proposition(
        "A vacina influenza protege 99% das pessoas com alergia ao ovo.",
        PropositionRole.CORE,
        PropositionType.FACT,
    )
    assert framed_post_rules(numeric, _raw("PARTIAL"), ALIASES).partial
    entailed = framed_post_rules(numeric, _raw("ENTAILED"), ALIASES)
    assert entailed.downgrade_reason is DowngradeReason.UNSUPPORTED_NUMBER


def test_without_partial_the_v5_aggregation_applies() -> None:
    entailed = FramedJudgment(CORE, Relation.ENTAILED, Relation.ENTAILED, QUOTE, "doc:p1:c1")
    contradicted = FramedJudgment(
        CORE, Relation.CONTRADICTED, Relation.CONTRADICTED, QUOTE, "doc:p1:c1"
    )
    assert aggregate_verdict_v7([entailed]) is Verdict.SUPPORTED
    assert aggregate_verdict_v7([contradicted]) is Verdict.REFUTED
    plain = PropositionJudgment(CORE, Relation.NOT_ADDRESSED, Relation.NOT_ADDRESSED)
    assert aggregate_verdict_v7([plain]) is Verdict.INSUFFICIENT_EVIDENCE


def test_invalid_relation_raises() -> None:
    with pytest.raises(ModelOutputError):
        framed_post_rules(CORE, _raw("MAYBE"), ALIASES)


class _FakeClient:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[dict[str, Any]] = []

    def chat(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return self.payload


def test_framing_judge_sends_partial_in_schema_and_prompt() -> None:
    client = _FakeClient({"judgments": [_raw("PARTIAL")]})
    (judgment,) = FramingPropositionJudge(client).judge([CORE], [CHUNK])
    assert judgment.partial
    call = client.calls[0]
    assert call["system_prompt"] == FRAMING_SYSTEM_PROMPT
    relations = call["schema"]["properties"]["judgments"]["items"]["properties"]["relation"]
    assert "PARTIAL" in relations["enum"]


def test_framing_judge_without_evidence_does_not_call_the_model() -> None:
    client = _FakeClient({})
    (judgment,) = FramingPropositionJudge(client).judge([CORE], [])
    assert judgment.relation is Relation.NOT_ADDRESSED and not client.calls
