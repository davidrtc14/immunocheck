from __future__ import annotations

from dataclasses import replace

from immunocheck.application.text_components import PERSONAL_MEDICAL_ADVICE
from immunocheck.domain.models import FactCheckResult, Verdict

INDIVIDUAL_ADVICE_REFUSAL = (
    "A resposta gerada continha orientação individual de saúde, que este sistema não "
    "oferece. Procure um profissional de saúde para decisões sobre o seu caso."
)


def contains_individual_advice(result: FactCheckResult) -> bool:
    """Procura orientação individual nos campos gerados; a alegação do usuário é ignorada."""
    generated = (result.explanation, result.correct_fact, result.omitted_or_distorted)
    return any(
        pattern.search(text)
        for text in generated
        if text
        for pattern in PERSONAL_MEDICAL_ADVICE
    )


def enforce_no_individual_advice(result: FactCheckResult) -> FactCheckResult:
    """Pós-filtro determinístico: substitui a saída por abstenção segura se houver orientação."""
    if not contains_individual_advice(result):
        return result
    return replace(
        result,
        verdict=Verdict.INSUFFICIENT_EVIDENCE,
        explanation=INDIVIDUAL_ADVICE_REFUSAL,
        correct_fact=None,
        omitted_or_distorted=None,
        sources=(),
    )
