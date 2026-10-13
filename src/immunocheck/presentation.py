from __future__ import annotations

from immunocheck.domain.models import FactCheckResult, Verdict

VERDICT_LABELS = {
    Verdict.SUPPORTED: "SUSTENTADA",
    Verdict.REFUTED: "REFUTADA",
    Verdict.MISLEADING: "ENGANOSA",
    Verdict.INSUFFICIENT_EVIDENCE: "EVIDÊNCIA INSUFICIENTE",
}

MEDICAL_DISCLAIMER = (
    "Esta análise compara uma alegação com fontes documentais e não substitui "
    "orientação de um profissional de saúde."
)


def format_result(result: FactCheckResult, *, elapsed_seconds: float) -> str:
    lines = [
        f"VEREDITO: {VERDICT_LABELS[result.verdict]}",
        f"ALEGAÇÃO ANALISADA: {result.claim or 'não identificada'}",
    ]
    if result.multiple_claims_detected:
        lines.append(
            "ESCOPO: O conteúdo contém múltiplas alegações; esta versão analisou somente a principal."
        )
    lines.append(f"EXPLICAÇÃO: {result.explanation}")
    if result.correct_fact:
        lines.append(f"FATO CORRETO: {result.correct_fact}")
    if result.omitted_or_distorted:
        lines.append(f"OMISSÃO OU DISTORÇÃO: {result.omitted_or_distorted}")
    if result.sources:
        source_heading = (
            "FONTES CONSULTADAS (não conclusivas):"
            if result.verdict is Verdict.INSUFFICIENT_EVIDENCE
            else "FONTES:"
        )
        lines.append(source_heading)
        for position, source in enumerate(result.sources, start=1):
            details = [source.source_name, source.document_title]
            if source.publication_date:
                details.append(source.publication_date)
            if source.section:
                details.append(source.section)
            elif source.page:
                details.append(f"p. {source.page}")
            lines.append(f"  [{position}] {' — '.join(details)}")
            lines.append(f"      {source.url}")
    else:
        lines.append("FONTES: nenhuma fonte suficiente para sustentar uma conclusão.")
    lines.extend(
        (
            f"AVISO: {MEDICAL_DISCLAIMER}",
            f"TEMPO TOTAL: {elapsed_seconds:.2f} s",
        )
    )
    return "\n".join(lines)
