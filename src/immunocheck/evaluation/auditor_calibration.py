from __future__ import annotations

from collections.abc import Mapping

from immunocheck.domain.models import DraftVerdict, Verdict, VerificationReport
from immunocheck.evaluation.end_to_end import EndToEndDatasetError


def draft_from_condition(condition: Mapping[str, object]) -> DraftVerdict:
    try:
        verdict = Verdict(condition["verdict"])
        explanation = condition["explanation"]
        source_ids = condition["source_ids"]
        correct_fact = condition.get("correct_fact")
        omitted = condition.get("omitted_or_distorted")
    except (KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError("Condição densa não contém rascunho válido.") from exc
    if not isinstance(explanation, str) or not explanation.strip():
        raise EndToEndDatasetError("Explicação ausente na condição densa.")
    if not isinstance(source_ids, list) or any(not isinstance(item, str) for item in source_ids):
        raise EndToEndDatasetError("Citações inválidas na condição densa.")
    if correct_fact is not None and not isinstance(correct_fact, str):
        raise EndToEndDatasetError("Fato correto inválido na condição densa.")
    if omitted is not None and not isinstance(omitted, str):
        raise EndToEndDatasetError("Omissão ou distorção inválida na condição densa.")
    return DraftVerdict(
        verdict=verdict,
        explanation=explanation,
        source_ids=tuple(source_ids),
        correct_fact=correct_fact,
        omitted_or_distorted=omitted,
    )


def apply_audit_result(
    condition: Mapping[str, object],
    *,
    report: VerificationReport | None,
    audit_latency_ms: float,
    technical_error: str | None = None,
) -> dict[str, object]:
    candidate = dict(condition)
    try:
        candidate["latency_ms"] = float(condition["latency_ms"]) + audit_latency_ms
    except (KeyError, TypeError, ValueError) as exc:
        raise EndToEndDatasetError("Latência inválida na condição densa.") from exc
    candidate["auditor_invoked"] = report is not None or technical_error is not None
    candidate["auditor_approved"] = report.all_supported if report is not None else None
    candidate["auditor_unsupported_sentences"] = (
        list(report.unsupported_sentences) if report is not None else []
    )
    candidate["technical_error"] = technical_error or condition.get("technical_error")

    if technical_error is not None:
        candidate.update(
            verdict=Verdict.INSUFFICIENT_EVIDENCE.value,
            explanation="Falha técnica durante a avaliação local.",
            correct_fact=None,
            omitted_or_distorted=None,
            source_ids=[],
        )
    elif report is not None and not report.all_supported:
        candidate.update(
            verdict=Verdict.INSUFFICIENT_EVIDENCE.value,
            explanation=(
                "As fontes recuperadas não permitem avaliar com segurança todas as partes da "
                "alegação."
            ),
            correct_fact=None,
            omitted_or_distorted=None,
        )
    return candidate
