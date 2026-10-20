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

# A análise de erros da v7 mostrou que a maior parte das abstenções em alegações reais vem de casos
# individuais, fatos políticos ou institucionais e conspirações que documentos técnicos não tratam.
# A orientação é fixa: não depende do motivo interno da abstenção nem altera o veredito.
INSUFFICIENT_GUIDANCE = (
    (
        "O QUE ISSO SIGNIFICA: as fontes do ImmunoCheck não permitem confirmar nem descartar a "
        "alegação. Isso não quer dizer que ela seja verdadeira nem falsa."
    ),
    (
        "  - Relatos de casos individuais, como alguém que passou mal após uma vacina, não são "
        "confirmados por documentos oficiais. Suspeitas de evento adverso devem ser comunicadas a "
        "uma unidade de saúde, que faz a notificação à vigilância."
    ),
    (
        "  - Notícias, declarações de pessoas e fatos políticos estão fora do alcance das fontes "
        "técnicas; agências de checagem jornalística são o caminho mais adequado."
    ),
    "  - Se a alegação for sobre vacinas em geral, tente reformulá-la em uma única frase objetiva.",
)
NO_CLAIM_GUIDANCE = (
    (
        'COMO ENVIAR: escreva uma única afirmação sobre vacinação humana, por exemplo: "A vacina da '
        'gripe pode ser aplicada em gestantes." Perguntas, opiniões e textos sem uma afirmação '
        "verificável não podem ser checados."
    ),
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
    if result.verdict is Verdict.INSUFFICIENT_EVIDENCE:
        lines.extend(NO_CLAIM_GUIDANCE if result.claim is None else INSUFFICIENT_GUIDANCE)
    lines.extend(
        (
            f"AVISO: {MEDICAL_DISCLAIMER}",
            f"TEMPO TOTAL: {elapsed_seconds:.2f} s",
        )
    )
    return "\n".join(lines)
