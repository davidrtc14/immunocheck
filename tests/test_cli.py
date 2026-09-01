from immunocheck.domain.models import FactCheckResult, SourceReference, Verdict
from immunocheck.presentation import MEDICAL_DISCLAIMER, format_result


def test_formats_programmatic_citations_and_fixed_disclaimer() -> None:
    result = FactCheckResult(
        verdict=Verdict.SUPPORTED,
        explanation="A fonte sustenta a alegação.",
        claim="A vacina está indicada.",
        sources=(
            SourceReference(
                chunk_id="chunk-1",
                source_name="Ministério da Saúde",
                document_title="Calendário Nacional",
                url="https://www.gov.br/saude/calendario.pdf",
                publication_date="2026-01-01",
                page=10,
            ),
        ),
    )

    output = format_result(result, elapsed_seconds=1.25)

    assert "VEREDITO: SUSTENTADA" in output
    assert "Calendário Nacional" in output
    assert "p. 10" in output
    assert "https://www.gov.br/saude/calendario.pdf" in output
    assert MEDICAL_DISCLAIMER in output


def test_formats_scope_notice_and_non_conclusive_sources() -> None:
    result = FactCheckResult.insufficient(
        "As fontes cobrem somente parte da alegação.",
        claim="Alegação principal.",
        sources=(
            SourceReference(
                chunk_id="chunk-1",
                source_name="Ministério da Saúde",
                document_title="Manual de vacinação",
                url="https://example.gov.br/manual",
            ),
        ),
        multiple_claims_detected=True,
    )

    output = format_result(result, elapsed_seconds=2.0)

    assert "ESCOPO: O conteúdo contém múltiplas alegações" in output
    assert "FONTES CONSULTADAS (não conclusivas):" in output
