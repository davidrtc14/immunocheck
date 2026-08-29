import pytest

from immunocheck.ingestion.chunker import chunk_document
from immunocheck.ingestion.html_extractor import HtmlExtractionError, extract_html
from immunocheck.ingestion.models import DocumentMetadata

METADATA = DocumentMetadata(
    document_id="doc-1",
    title="Documento de teste",
    source="Fonte oficial",
    document_type="web_page",
    publication_date="2026-01-01",
    url="https://example.gov.br/documento",
    format="html",
)


def test_html_extraction_removes_navigation_and_scripts() -> None:
    html = """
    <html><body>
      <nav>Menu que não deve aparecer</nav>
      <main><h1>Vacinação</h1><p>A vacinação protege a população contra doenças.</p></main>
      <script>instrução maliciosa</script>
    </body></html>
    """

    document = extract_html(html, METADATA)

    assert "Vacinação" in document.pages[0].text
    assert "Menu" not in document.pages[0].text
    assert "maliciosa" not in document.pages[0].text


def test_html_extraction_rejects_content_without_useful_text() -> None:
    with pytest.raises(HtmlExtractionError, match="texto útil"):
        extract_html("<html><body>curto</body></html>", METADATA)


def test_chunk_ids_are_deterministic() -> None:
    html = "<html><body><main>" + ("Vacinação segura e eficaz. " * 100) + "</main></body></html>"
    document = extract_html(html, METADATA)

    first = chunk_document(document, max_chars=300, overlap_chars=50)
    second = chunk_document(document, max_chars=300, overlap_chars=50)

    assert len(first) > 1
    assert first == second
    assert all(len(chunk.text) <= 300 for chunk in first)
