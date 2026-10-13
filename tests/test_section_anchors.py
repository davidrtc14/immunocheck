from __future__ import annotations

import json

import pytest

from immunocheck.domain.models import FactCheckResult, SourceReference, Verdict
from immunocheck.ingestion.chunker import chunk_document
from immunocheck.ingestion.html_extractor import extract_html
from immunocheck.ingestion.models import (
    DocumentMetadata,
    ExtractedDocument,
    ExtractedPage,
)
from immunocheck.ingestion.xml_extractor import extract_xml
from immunocheck.presentation import format_result
from immunocheck.retrieval.pilot_corpus import CorpusLoadError, load_evidence_jsonl


def _metadata(fmt: str) -> DocumentMetadata:
    return DocumentMetadata(
        document_id="doc",
        title="Documento",
        source="Fonte",
        document_type="guideline",
        publication_date="2024-01-01",
        url="https://example.gov.br/doc",
        format=fmt,
    )


HTML = (
    "<html><body><main><h1>Vacinas</h1>"
    + "<p>" + "Introdução sobre vacinas seguras. " * 60 + "</p>"
    + "<h2>Eventos adversos</h2>"
    + "<p>" + "Eventos adversos são raros e monitorados. " * 60 + "</p>"
    + "</main></body></html>"
)


def test_html_chunks_cite_nearest_heading_and_paragraph() -> None:
    document = extract_html(HTML, _metadata("html"))
    chunks = chunk_document(document, max_chars=500, overlap_chars=50)

    assert chunks[0].section == "Vacinas, §1" or chunks[0].section == "Vacinas, §2"
    assert {chunk.page_start for chunk in chunks} == {1}
    sections = [chunk.section for chunk in chunks]
    assert any(section and section.startswith("Eventos adversos, §") for section in sections)
    assert all(section is not None for section in sections)


def test_chunk_ids_do_not_depend_on_section_anchor() -> None:
    document = extract_html(HTML, _metadata("html"))
    bare = ExtractedDocument(
        metadata=document.metadata,
        pages=(ExtractedPage(number=1, text=document.pages[0].text),),
    )
    with_anchor = chunk_document(document, max_chars=500, overlap_chars=50)
    without_anchor = chunk_document(bare, max_chars=500, overlap_chars=50)
    assert [c.chunk_id for c in with_anchor] == [c.chunk_id for c in without_anchor]
    assert all(c.section is not None for c in with_anchor)


def test_heading_is_not_assigned_before_it_appears() -> None:
    html = (
        "<main><p>Parágrafo inicial longo o suficiente para ser texto útil agora.</p>"
        "<h2>Seção</h2><p>Conteúdo da seção.</p></main>"
    )
    chunks = chunk_document(extract_html(html, _metadata("html")), max_chars=40, overlap_chars=0)
    assert chunks[0].section == "§1"
    assert chunks[-1].section.startswith("Seção, §")


def test_pdf_chunks_have_no_section() -> None:
    document = ExtractedDocument(
        metadata=_metadata("pdf"),
        pages=(ExtractedPage(number=3, text="Texto de PDF. " * 20),),
    )
    chunks = chunk_document(document)
    assert all(chunk.section is None and chunk.page_start == 3 for chunk in chunks)


def test_xml_titles_become_section_headings() -> None:
    xml = (
        "<article><front><article-title>Estudo de segurança vacinal</article-title></front>"
        "<body><sec><title>Métodos</title><p>Descrição dos métodos utilizados no estudo.</p>"
        "</sec><sec><title>Resultados</title><p>Os resultados mostram segurança adequada.</p>"
        "</sec></body></article>"
    )
    document = extract_xml(xml, _metadata("xml"))
    chunks = chunk_document(document, max_chars=30, overlap_chars=0)
    labels = [chunk.section for chunk in chunks]
    assert any(label and label.startswith("Métodos, §") for label in labels)
    assert any(label and label.startswith("Resultados, §") for label in labels)


def test_xml_extractor_handles_deep_documents_linearly() -> None:
    paragraphs = "".join(f"<p>Parágrafo número {i} com texto suficiente.</p>" for i in range(3000))
    document = extract_xml(f"<article><body>{paragraphs}</body></article>", _metadata("xml"))
    assert document.pages[0].text.count("\n") == 2999


def _write_chunk(path, **overrides) -> None:
    row = {
        "chunk_id": "doc:p1:c1:abc",
        "text": "Texto",
        "source": "Fonte",
        "document_title": "Doc",
        "url": "https://example.gov.br/doc",
        "publication_date": None,
        "page_start": 1,
    }
    row.update(overrides)
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")


def test_corpus_loader_reads_optional_section(tmp_path) -> None:
    path = tmp_path / "chunks.jsonl"
    _write_chunk(path, section="Vacinas, §4")
    assert load_evidence_jsonl(path)[0].section == "Vacinas, §4"
    _write_chunk(path)
    assert load_evidence_jsonl(path)[0].section is None
    _write_chunk(path, section=7)
    with pytest.raises(CorpusLoadError):
        load_evidence_jsonl(path)


def test_presentation_prefers_section_over_page() -> None:
    def render(section: str | None) -> str:
        source = SourceReference(
            chunk_id="c",
            source_name="Fonte",
            document_title="Doc",
            url="https://example.gov.br/doc",
            page=1,
            section=section,
        )
        result = FactCheckResult(Verdict.SUPPORTED, "Ok.", claim="x", sources=(source,))
        return format_result(result, elapsed_seconds=1.0)

    assert "Vacinas, §4" in render("Vacinas, §4")
    assert "p. 1" not in render("Vacinas, §4")
    assert "p. 1" in render(None)
