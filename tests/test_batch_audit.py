from __future__ import annotations

import csv
import hashlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from immunocheck.ingestion.batch_audit import audit_download
from immunocheck.ingestion.catalog import CatalogEntry
from immunocheck.ingestion.downloader import DownloadReceipt
from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage
from scripts import audit_corpus_batch


@pytest.fixture
def sample(tmp_path: Path) -> tuple[CatalogEntry, DownloadReceipt]:
    content = (
        "<html><main><h1>Documento sintético para teste de extração</h1>"
        "<p>Este conteúdo não é uma fonte médica.</p></main><footer>"
        "Todos os direitos reservados. Creative Commons "
        '<a href="https://creativecommons.org/licenses/by-nd/3.0/">Licença</a>'
        "</footer></html>"
    ).encode()
    (tmp_path / "synthetic.html").write_bytes(content)
    entry = CatalogEntry(
        DocumentMetadata(
            "synthetic",
            "Documento sintético",
            "Teste",
            "web_page",
            None,
            "https://example.gov.br/synthetic",
            "html",
        ),
        "vacinas_especificas",
        "2026-09-06",
        "to_verify",
        "downloaded",
        "Apenas teste",
    )
    receipt = DownloadReceipt(
        "synthetic",
        "synthetic.html",
        hashlib.sha256(content).hexdigest(),
        len(content),
        "text/html",
        entry.metadata.url,
        entry.metadata.url,
        "2026-09-06T18:00:00-03:00",
    )
    return entry, receipt


def test_audit_examines_footer_without_granting_permission(sample, tmp_path):
    entry, receipt = sample
    report, document = audit_download(entry, receipt, tmp_path)
    assert "todos os direitos reservados" in report["license_signals_not_permission"]
    assert report["license_links"] == ["https://creativecommons.org/licenses/by-nd/3.0/"]
    assert "reservados" not in document.pages[0].text
    assert report["human_review"] == "pending"
    assert entry.status == "downloaded"
    assert report["raw_sha256"] == receipt.sha256
    assert report["pages"] == 1
    assert report["chunks"] > 0
    assert report["characters"] == len(document.pages[0].text)
    assert "content" not in report and "text" not in report


@pytest.mark.parametrize(
    "change, message",
    [
        ({"sha256": "0" * 64}, "SHA-256"),
        ({"size_bytes": 0}, "Tamanho"),
        ({"document_id": "other"}, "corresponde"),
        ({"source_url": "https://example.gov.br/other"}, "corresponde"),
        ({"relative_path": "../outside.html"}, "fora"),
    ],
)
def test_audit_rejects_invalid_receipt(sample, tmp_path, change, message):
    entry, receipt = sample
    with pytest.raises(ValueError, match=message):
        audit_download(entry, replace(receipt, **change), tmp_path)


def test_audit_rejects_unsafe_document_id(sample, tmp_path):
    entry, receipt = sample
    entry = replace(entry, metadata=replace(entry.metadata, document_id="../unsafe"))
    with pytest.raises(ValueError, match="inseguro"):
        audit_download(entry, receipt, tmp_path)


def test_audit_pdf_preserves_empty_page_warnings(sample, tmp_path, monkeypatch):
    entry, receipt = sample
    entry = replace(entry, metadata=replace(entry.metadata, format="pdf"))
    document = ExtractedDocument(
        entry.metadata,
        (
            ExtractedPage(1, "Texto sintético sem informação clínica.\ufffd\x02"),
            ExtractedPage(2, ""),
        ),
        ("Página 2 sem texto",),
    )
    monkeypatch.setattr("immunocheck.ingestion.batch_audit.extract_pdf", lambda *_: document)
    report, _ = audit_download(entry, receipt, tmp_path)
    assert report["empty_pages"] == [2]
    assert report["warnings"] == ["Página 2 sem texto"]
    assert report["replacement_characters"] == 1
    assert report["control_characters"] == 1


def test_audit_extracts_jats_xml_and_namespaced_license_link(tmp_path: Path) -> None:
    content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <article xmlns:xlink="http://www.w3.org/1999/xlink">
      <front><article-meta><title-group><article-title>Revisao sintetica</article-title>
      </title-group><permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/">
      <license-p>Creative Commons Attribution.</license-p></license></permissions>
      <abstract><p>Texto suficientemente longo para uma auditoria de extracao.</p></abstract>
      </article-meta></front>
    </article>"""
    (tmp_path / "synthetic.xml").write_bytes(content)
    metadata = DocumentMetadata(
        "synthetic-xml",
        "Documento XML sintético",
        "Teste",
        "systematic_review",
        None,
        "https://example.org/synthetic.xml",
        "xml",
    )
    entry = CatalogEntry(
        metadata,
        "eficacia_e_imunogenicidade",
        "2026-09-09",
        "CC-BY-4.0",
        "downloaded",
        "Apenas teste",
    )
    receipt = DownloadReceipt(
        metadata.document_id,
        "synthetic.xml",
        hashlib.sha256(content).hexdigest(),
        len(content),
        "application/xml",
        metadata.url,
        metadata.url,
        "2026-09-09T18:00:00-03:00",
    )

    report, document = audit_download(entry, receipt, tmp_path)

    assert "Revisao sintetica" in document.pages[0].text
    assert report["license_links"] == ["https://creativecommons.org/licenses/by/4.0/"]
    assert "creative commons" in report["license_signals_not_permission"]


def test_batch_script_reports_missing_receipt_without_publishing(sample, tmp_path, monkeypatch):
    entry, receipt = sample
    corpus = tmp_path / "corpus"
    raw = corpus / "raw"
    reviews = corpus / "reviews"
    raw.mkdir(parents=True)
    reviews.mkdir()
    (raw / "synthetic.html").write_bytes((tmp_path / "synthetic.html").read_bytes())
    (raw / "downloads.json").write_text(json.dumps([asdict(receipt)]), encoding="utf-8")
    missing = replace(entry, metadata=replace(entry.metadata, document_id="missing"))
    with (corpus / "catalog.csv").open("w", newline="", encoding="utf-8") as file:
        rows = [
            asdict(value.metadata)
            | {
                "primary_theme": value.primary_theme,
                "access_date": value.access_date,
                "license_status": value.license_status,
                "status": value.status,
                "notes": value.notes,
            }
            for value in (entry, missing)
        ]
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    review_path = reviews / "batch_999.csv"
    review_path.write_text("document_id\nsynthetic\nmissing\n", encoding="utf-8")
    catalog_before = (corpus / "catalog.csv").read_bytes()
    reviews_before = review_path.read_bytes()
    monkeypatch.setattr(audit_corpus_batch, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["audit_corpus_batch", "--batch", "999"])
    with pytest.raises(SystemExit) as exc:
        audit_corpus_batch.main()
    assert exc.value.code == 1
    report = json.loads((reviews / "batch_999.audit.json").read_text(encoding="utf-8"))
    assert len(report["documents"]) == 1
    assert report["failures"][0]["document_id"] == "missing"
    assert report["exact_text_duplicates_within_batch"] == []
    assert (raw / "reviews" / "batch_999" / "synthetic.txt").exists()
    assert (corpus / "catalog.csv").read_bytes() == catalog_before
    assert review_path.read_bytes() == reviews_before
    assert not (corpus / "processed").exists()
