from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from immunocheck.application.proposition_nli import DowngradeReason, Relation
from immunocheck.application.structured_claim import (
    Proposition,
    PropositionRole,
    PropositionType,
)
from immunocheck.application.text_components import ModelOutputError
from immunocheck.application.tolerant_verification import (
    TolerantPropositionJudge,
    apply_tolerant_post_rules,
    number_values,
    quote_matches,
    unsupported_numbers,
)
from immunocheck.domain.models import Evidence

CHUNK = (
    "Em 2010, a vacina contra rotavírus evitou cerca de 28 mil mortes de crianças menores de "
    "5 anos, segundo estimativas publicadas em revista científica."
)


def _evidence(text: str = CHUNK, chunk_id: str = "doc:p1:c1") -> Evidence:
    return Evidence(
        chunk_id=chunk_id,
        source_name="Fonte",
        document_title="Documento",
        publication_date="2026-01-01",
        url="https://example.org",
        text=text,
        retrieval_score=1.0,
    )


def _proposition(text: str) -> Proposition:
    return Proposition(text=text, role=PropositionRole.CORE, type=PropositionType.FACT)


def test_exact_and_slightly_reworded_quotes_match() -> None:
    assert quote_matches("a vacina contra rotavírus evitou cerca de 28 mil mortes", CHUNK)
    # Uma palavra trocada em 13: cobertura de 12/13 > 90%.
    assert quote_matches(
        "Em 2010 a vacina contra rotavirus evitou cerca de 28 mil obitos de criancas menores",
        CHUNK,
    )


def test_unrelated_or_short_quotes_do_not_match() -> None:
    assert not quote_matches("a vacina contra sarampo causou milhares de mortes em 2010", CHUNK)
    assert not quote_matches("evitou mortes", CHUNK)


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("90,7%", 90.7),
        ("90.7 por cento", 90.7),
        ("28 mil mortes", 28_000.0),
        ("28.000 mortes", 28_000.0),
        ("setenta por cento", 70.0),
        ("1.234,5 doses", 1_234.5),
        ("2 milhões de doses", 2_000_000.0),
    ],
)
def test_number_values_read_equivalent_forms(text: str, value: float) -> None:
    assert value in number_values(text)


def test_single_decimal_separator_is_not_read_as_thousands() -> None:
    assert 907.0 not in number_values("90,7%")
    assert {28.0, 28_000.0} <= number_values("28.000")


def test_unsupported_numbers_accept_equivalents_and_flag_missing() -> None:
    assert unsupported_numbers("A vacina evitou 28.000 mortes em 2010.", CHUNK) == ()
    assert unsupported_numbers("A vacina evitou 35 mil mortes em 2010.", CHUNK) == ("35",)
    assert unsupported_numbers("A covid-19 tem 5 sintomas.", CHUNK) == ()


def test_multiplier_in_the_proposition_counts() -> None:
    evidence = "A vacina evitou cerca de 28 000 mortes de criancas em 2016."
    assert unsupported_numbers("A vacina evitou 28 mil mortes em 2016.", evidence) == ()
    assert unsupported_numbers("A vacina evitou 35 mil mortes em 2016.", evidence) == ("35",)


def test_space_grouping_does_not_merge_adjacent_numbers() -> None:
    assert 5_201.0 not in number_values("menores de 5 2016")
    assert {5.0, 2016.0} <= number_values("menores de 5 2016")


@pytest.mark.parametrize(
    "proposition",
    [
        "A vacina evitou 28 mil mortes em 2010.",
        "Foram 1.234 doses e 90,7% de cobertura em 2010.",
        "A cobertura chegou a 98% em 2024.",
    ],
)
def test_never_stricter_than_the_v5_number_rule(proposition: str) -> None:
    from immunocheck.application.proposition_nli import unsupported_numbers as strict

    for evidence in (CHUNK, "Cobertura de 98% em 2024 e 1234 doses.", "Nada aqui."):
        assert set(unsupported_numbers(proposition, evidence)) <= set(strict(proposition, evidence))


def test_post_rules_keep_tolerant_quotes_and_downgrade_missing_numbers() -> None:
    aliases = {"E1": _evidence()}
    quote = "a vacina contra rotavirus evitou cerca de 28 mil mortes de criancas menores"
    kept = apply_tolerant_post_rules(
        _proposition("A vacina evitou 28 mil mortes."),
        {"relation": "ENTAILED", "source_ref": "E1", "quote": quote},
        aliases,
    )
    assert kept.relation is Relation.ENTAILED and kept.source_id == "doc:p1:c1"
    number = apply_tolerant_post_rules(
        _proposition("A vacina evitou 90 mil mortes."),
        {"relation": "ENTAILED", "source_ref": "E1", "quote": quote},
        aliases,
    )
    assert number.downgrade_reason is DowngradeReason.UNSUPPORTED_NUMBER
    bad_ref = apply_tolerant_post_rules(
        _proposition("A vacina evitou 28 mil mortes."),
        {"relation": "CONTRADICTED", "source_ref": "E9", "quote": quote},
        aliases,
    )
    assert bad_ref.downgrade_reason is DowngradeReason.NO_VERIFIED_QUOTE
    with pytest.raises(ModelOutputError):
        apply_tolerant_post_rules(_proposition("x"), {"relation": "TALVEZ"}, aliases)


@dataclass
class FakeClient:
    payload: dict
    calls: list = field(default_factory=list)

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        return self.payload


def test_judge_reuses_v5_prompt_and_validation_with_tolerant_rules() -> None:
    quote = "Em 2010 a vacina contra rotavirus evitou cerca de 28 mil obitos de criancas menores"
    client = FakeClient(
        {
            "judgments": [
                {"proposition": "P1", "relation": "ENTAILED", "source_ref": "E1", "quote": quote}
            ]
        }
    )
    judgments = TolerantPropositionJudge(client).judge(
        [_proposition("A vacina evitou 28 mil mortes em 2010.")], [_evidence()]
    )
    assert judgments[0].relation is Relation.ENTAILED
    assert "proposi" in client.calls[0]["system_prompt"].lower()

    invalid = FakeClient({"judgments": []})
    with pytest.raises(ModelOutputError):
        TolerantPropositionJudge(invalid).judge([_proposition("x")], [_evidence()])


def test_judge_without_evidence_does_not_call_the_model() -> None:
    client = FakeClient({})
    judgments = TolerantPropositionJudge(client).judge([_proposition("x")], [])
    assert judgments[0].relation is Relation.NOT_ADDRESSED and client.calls == []
