from __future__ import annotations

from immunocheck.domain.models import FactCheckResult, Verdict

# Rótulos exibidos ao usuário. Os vereditos internos (e os do artigo) continuam sendo sustentada,
# refutada, enganosa e evidência insuficiente; só a apresentação usa termos do dia a dia.
VERDICT_LABELS = {
    Verdict.SUPPORTED: "✅ VERDADEIRO",
    Verdict.REFUTED: "❌ FALSO",
    Verdict.MISLEADING: "⚠️ ENGANOSO",
    Verdict.INSUFFICIENT_EVIDENCE: "🔍 NÃO DÁ PARA CONFIRMAR",
}
NO_CLAIM_LABEL = "❔ NENHUMA ALEGAÇÃO IDENTIFICADA"

# Frase curta sob o rótulo quando o resultado não traz um fato correto. Nada aqui é gerado pela LLM.
VERDICT_SUMMARIES = {
    Verdict.SUPPORTED: "Isso é verdade, de acordo com as fontes oficiais e científicas consultadas.",
    Verdict.REFUTED: "Isso não é verdade, de acordo com as fontes oficiais e científicas consultadas.",
    Verdict.MISLEADING: "Isso distorce o que dizem as fontes oficiais e científicas consultadas.",
    Verdict.INSUFFICIENT_EVIDENCE: (
        "As fontes consultadas não permitem dizer se isso é verdadeiro ou falso."
    ),
}
NO_CLAIM_SUMMARY = "Não encontrei uma afirmação sobre vacinas para verificar."

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
    """Resposta ao usuário: veredito e frase simples no topo; explicação formal e fontes abaixo."""

    no_claim = result.verdict is Verdict.INSUFFICIENT_EVIDENCE and result.claim is None
    lines = [NO_CLAIM_LABEL if no_claim else VERDICT_LABELS[result.verdict], _summary(result), ""]
    lines.append(f"📖 EXPLICAÇÃO: {result.explanation}")
    if result.omitted_or_distorted:
        lines.append(f"🔎 O QUE FOI DISTORCIDO: {result.omitted_or_distorted}")
    lines.append(f"📝 ALEGAÇÃO ANALISADA: {result.claim or 'não identificada'}")
    if result.multiple_claims_detected:
        lines.append(
            "📌 ESCOPO: O conteúdo contém múltiplas alegações; esta versão analisou somente a "
            "principal."
        )
    lines.append("")
    sources = _unique_sources(result)
    if sources:
        lines.append(
            "📚 FONTES CONSULTADAS (não conclusivas):"
            if result.verdict is Verdict.INSUFFICIENT_EVIDENCE
            else "📚 FONTES:"
        )
        for position, (description, url) in enumerate(sources, start=1):
            lines.append(f"  [{position}] {description}")
            lines.append(f"      {url}")
    else:
        lines.append("📚 FONTES: nenhuma fonte suficiente para sustentar uma conclusão.")
    if result.verdict is Verdict.INSUFFICIENT_EVIDENCE:
        lines.append("")
        lines.extend(NO_CLAIM_GUIDANCE if no_claim else INSUFFICIENT_GUIDANCE)
    lines.extend(
        (
            "",
            f"ℹ️ AVISO: {MEDICAL_DISCLAIMER}",
            f"⏱️ TEMPO TOTAL: {elapsed_seconds:.2f} s",
        )
    )
    return "\n".join(lines)


def _summary(result: FactCheckResult) -> str:
    """O fato correto já produzido pela pipeline, quando houver; senão, uma frase fixa."""

    if result.verdict is Verdict.INSUFFICIENT_EVIDENCE:
        return NO_CLAIM_SUMMARY if result.claim is None else VERDICT_SUMMARIES[result.verdict]
    if result.correct_fact and result.verdict in {Verdict.REFUTED, Verdict.MISLEADING}:
        return result.correct_fact
    return VERDICT_SUMMARIES[result.verdict]


def _unique_sources(result: FactCheckResult) -> list[tuple[str, str]]:
    """Fontes como exibidas, sem repetir trechos distintos do mesmo documento e da mesma página.

    Só a exibição muda: o veredito e as fontes do resultado continuam como a pipeline os produziu.
    """

    unique: list[tuple[str, str]] = []
    for source in result.sources:
        details = [source.source_name, source.document_title]
        if source.publication_date:
            details.append(source.publication_date)
        if source.section:
            details.append(source.section)
        elif source.page:
            details.append(f"p. {source.page}")
        entry = (" — ".join(details), source.url)
        if entry not in unique:
            unique.append(entry)
    return unique
