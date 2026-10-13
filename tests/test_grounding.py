from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from immunocheck.application.grounding import (
    UNGROUNDED_EXPLANATION,
    GroundedVerdictGenerator,
    alnum_key,
    verify_grounding,
)
from immunocheck.domain.models import DraftVerdict, Evidence, ExtractedClaim, Verdict

TEXT = (
    "Os dados mostram que a eficácia estimada foi de 90,7% em crianças de 5 a 11 anos, "
    "com intervalo de confiança amplo e circu- lação viral reduzida."
)
EVIDENCE = (
    Evidence("d:p1:c1:a", TEXT, "Fonte", "Doc", "https://x.gov.br/d"),
    Evidence(
        "d:p1:c2:b", "Outro trecho sem relação com a pergunta.", "Fonte", "Doc", "https://x.gov.br/d"
    ),
)
CLAIM = ExtractedClaim("Alegação.", 0.9)


def _draft(
    verdict=Verdict.SUPPORTED,
    explanation="A eficácia estimada foi de 90,7% nessa faixa.",
    **kw,
) -> DraftVerdict:
    return DraftVerdict(verdict, explanation, ("d:p1:c1:a",), **kw)


def test_literal_quote_with_formatting_noise_is_grounded() -> None:
    spans = [{"field": "explanation", "quote": "a eficácia estimada foi de 90,7% em crianças de 5 a 11 anos"}]
    assert verify_grounding(_draft(), EVIDENCE, spans).grounded
    hyphen = [{"field": "explanation", "quote": "intervalo de confiança amplo e circulação viral"}]
    assert verify_grounding(_draft(explanation="Intervalo amplo."), EVIDENCE, hyphen).grounded


def test_paraphrase_short_quote_or_wrong_chunk_is_not_grounded() -> None:
    quotes = (
        "a vacina funciona muito bem em crianças pequenas",
        "eficácia",
        "Outro trecho sem relação com a pergunta",
    )
    for quote in quotes:
        report = verify_grounding(_draft(), EVIDENCE, [{"field": "explanation", "quote": quote}])
        assert not report.grounded and report.missing_fields == ("explanation",)


def test_required_fields_depend_on_verdict() -> None:
    quote = {"field": "explanation", "quote": "a eficácia estimada foi de 90,7% em crianças"}
    refuted = _draft(Verdict.REFUTED, correct_fact="A eficácia foi de 90,7%.")
    assert verify_grounding(refuted, EVIDENCE, [quote]).missing_fields == ("correct_fact",)
    both = [quote, {"field": "correct_fact", "quote": "intervalo de confiança amplo"}]
    assert verify_grounding(refuted, EVIDENCE, both).grounded
    misleading = _draft(Verdict.MISLEADING, omitted_or_distorted="Omite o intervalo.")
    assert verify_grounding(misleading, EVIDENCE, [quote]).missing_fields == (
        "omitted_or_distorted",
    )


def test_invented_numbers_are_flagged_even_with_valid_quote() -> None:
    quote = [{"field": "explanation", "quote": "a eficácia estimada foi de 90,7% em crianças"}]
    report = verify_grounding(_draft(explanation="A eficácia foi de 95,2%."), EVIDENCE, quote)
    assert not report.grounded and report.unsupported_numbers == ("95,2",)


def test_abstention_and_uncited_drafts() -> None:
    abstention = DraftVerdict(Verdict.INSUFFICIENT_EVIDENCE, "Sem dados.", ())
    assert verify_grounding(abstention, EVIDENCE, []).grounded
    uncited = DraftVerdict(Verdict.SUPPORTED, "Ok.", ())
    assert verify_grounding(uncited, EVIDENCE, []).missing_fields == ("source_ids",)
    assert alnum_key("Circu- lação, 90,7%") == "circulacao907"


@dataclass
class FakeClient:
    spans: list[dict[str, Any]]
    seen: list[dict[str, Any]] = field(default_factory=list)

    def chat(self, *, system_prompt, user_prompt, schema, max_output_tokens) -> dict[str, Any]:
        self.seen.append({"system": system_prompt, "schema": schema, "max": max_output_tokens})
        return {"support_spans": self.spans}


class InnerGenerator:
    def __init__(self, client) -> None:
        self.client = client

    def generate(self, claim, evidence) -> DraftVerdict:
        self.client.chat(
            system_prompt="S",
            user_prompt="U",
            schema={"properties": {}, "required": []},
            max_output_tokens=10,
        )
        return _draft()


def test_wrapper_extends_schema_and_downgrades_ungrounded_output() -> None:
    quote = "a eficácia estimada foi de 90,7% em crianças"
    good = FakeClient([{"field": "explanation", "quote": quote}])
    draft = GroundedVerdictGenerator(good, InnerGenerator).generate(CLAIM, EVIDENCE)
    assert draft.verdict is Verdict.SUPPORTED
    assert "support_spans" in good.seen[0]["schema"]["properties"]
    assert "support_spans" in good.seen[0]["schema"]["required"]
    assert "LITERAL" in good.seen[0]["system"] and good.seen[0]["max"] == 266

    bad = FakeClient([{"field": "explanation", "quote": "trecho que o modelo inventou do nada"}])
    downgraded = GroundedVerdictGenerator(bad, InnerGenerator).generate(CLAIM, EVIDENCE)
    assert downgraded.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert downgraded.explanation == UNGROUNDED_EXPLANATION
    assert downgraded.source_ids == ("d:p1:c1:a",)
