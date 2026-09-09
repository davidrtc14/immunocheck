import pytest

from immunocheck.ingestion.models import DocumentMetadata
from immunocheck.ingestion.xml_extractor import XmlExtractionError, extract_xml

METADATA = DocumentMetadata(
    document_id="article-1",
    title="Artigo de teste",
    source="Repositório científico",
    document_type="systematic_review",
    publication_date="2026-01-01",
    url="https://example.org/article.xml",
    format="xml",
)


def test_xml_extraction_preserves_article_blocks_without_duplicate_nested_text() -> None:
    xml = """
    <article><front><article-meta><title-group><article-title>Vacinação</article-title>
    </title-group><abstract><p>Evidência sobre segurança e eficácia.</p></abstract>
    </article-meta></front><body><sec><title>Resultados</title>
    <p>A revisão encontrou resultados contextualizados.</p></sec></body></article>
    """

    document = extract_xml(xml, METADATA)

    text = document.pages[0].text
    assert "Vacinação" in text
    assert "Resultados" in text
    assert text.count("Evidência sobre segurança e eficácia.") == 1
    assert "Vacinação\nEvidência" in text


def test_xml_extraction_keeps_table_cells_separate() -> None:
    xml = """
    <article><body><table-wrap><caption><title>Desfechos</title></caption>
    <table><tr><th>Grupo</th><th>Resultado</th></tr>
    <tr><td>Vacina</td><td>Proteção observada</td></tr></table></table-wrap></body></article>
    """

    document = extract_xml(xml, METADATA)

    assert document.pages[0].text.splitlines() == [
        "Desfechos",
        "Grupo",
        "Resultado",
        "Vacina",
        "Proteção observada",
    ]


def test_xml_extraction_rejects_invalid_document() -> None:
    with pytest.raises(XmlExtractionError, match="inválido"):
        extract_xml("<article>", METADATA)
