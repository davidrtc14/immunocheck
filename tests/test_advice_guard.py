from __future__ import annotations

import pytest

from immunocheck.application.advice_guard import (
    INDIVIDUAL_ADVICE_REFUSAL,
    enforce_no_individual_advice,
)
from immunocheck.domain.models import FactCheckResult, SourceReference, Verdict
from tests.test_routed_pipeline import (
    CORPUS,
    Generator,
    _pipeline,
    _submission,
)

SOURCE = SourceReference.from_evidence(CORPUS[0])


def _result(**overrides: object) -> FactCheckResult:
    values: dict[str, object] = {
        "verdict": Verdict.REFUTED,
        "explanation": "A vacina integra o calendário nacional.",
        "claim": "Você deve tomar a vacina.",
        "correct_fact": "A vacina é segura segundo a fonte.",
        "sources": (SOURCE,),
    }
    values.update(overrides)
    return FactCheckResult(**values)  # type: ignore[arg-type]


def test_clean_result_is_returned_unchanged() -> None:
    result = _result()
    assert enforce_no_individual_advice(result) is result


@pytest.mark.parametrize(
    "field",
    ["explanation", "correct_fact", "omitted_or_distorted"],
)
@pytest.mark.parametrize(
    "advice",
    [
        "No seu caso você deve tomar a segunda dose.",
        "Interrompa o uso imediatamente.",
        "Você tem uma contraindicação.",
    ],
)
def test_individual_advice_in_generated_fields_becomes_abstention(
    field: str, advice: str
) -> None:
    guarded = enforce_no_individual_advice(_result(**{field: advice}))

    assert guarded.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert guarded.explanation == INDIVIDUAL_ADVICE_REFUSAL
    assert guarded.correct_fact is None
    assert guarded.omitted_or_distorted is None
    assert guarded.sources == ()
    assert guarded.claim == "Você deve tomar a vacina."


def test_user_claim_is_not_inspected() -> None:
    result = _result(claim="Tome a vacina agora, você tem que aplicar.")
    assert enforce_no_individual_advice(result) is result


def test_routed_pipeline_applies_guard_to_final_result() -> None:
    class AdvisingGenerator(Generator):
        def generate(self, claim, evidence):  # type: ignore[no-untyped-def]
            draft = super().generate(claim, evidence)
            return type(draft)(
                verdict=draft.verdict,
                explanation="Tome a vacina hoje.",
                source_ids=draft.source_ids,
            )

    result = _pipeline("GENERAL_SIMPLE", direct=AdvisingGenerator()).run(_submission())

    assert result.verdict is Verdict.INSUFFICIENT_EVIDENCE
    assert result.explanation == INDIVIDUAL_ADVICE_REFUSAL
    assert result.sources == ()
