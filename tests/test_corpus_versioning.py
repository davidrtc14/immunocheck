from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from immunocheck.ingestion.catalog import CatalogEntry
from immunocheck.ingestion.corpus_versioning import (
    CorpusVersioningError,
    build_corpus_snapshot,
    load_published_corpus,
    publish_corpus_snapshot,
)
from immunocheck.ingestion.downloader import DownloadReceipt
from immunocheck.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage


def _entry(document_id: str, *, title: str = "Documento") -> CatalogEntry:
    return CatalogEntry(
        metadata=DocumentMetadata(
            document_id=document_id,
            title=title,
            source="Fonte oficial",
            document_type="manual",
            publication_date="2026-01-01",
            url=f"https://example.gov.br/{document_id}.pdf",
            format="pdf",
        ),
        primary_theme="seguranca_e_farmacovigilancia",
        access_date="2026-08-31",
        license_status="uso institucional a verificar",
        status="validated",
        notes="teste",
    )


def _receipt(raw_dir: Path, document_id: str, content: bytes) -> DownloadReceipt:
    path = raw_dir / f"{document_id}.pdf"
    path.write_bytes(content)
    return DownloadReceipt(
        document_id=document_id,
        relative_path=path.name,
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        content_type="application/pdf",
        source_url=f"https://example.gov.br/{document_id}.pdf",
        final_url=f"https://cdn.example.gov.br/{document_id}.pdf",
        downloaded_at="2026-08-31T12:00:00+00:00",
    )


class RecordingExtractor:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, path: Path, entry: CatalogEntry) -> ExtractedDocument:
        self.calls.append(entry.metadata.document_id)
        text = f"Vacinação humana e evidência oficial. {path.read_bytes().decode()} " * 8
        return ExtractedDocument(
            metadata=entry.metadata,
            pages=(ExtractedPage(number=1, text=text),),
        )


def _publish(snapshot, processed_dir: Path) -> tuple[Path, Path]:
    chunks_path = processed_dir / "chunks.jsonl"
    manifest_path = processed_dir / "manifest.json"
    publish_corpus_snapshot(
        snapshot,
        chunks_path=chunks_path,
        report_path=processed_dir / "validation_report.json",
        manifest_path=manifest_path,
    )
    return chunks_path, manifest_path


def test_snapshot_records_provenance_and_has_deterministic_version(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    entry = _entry("doc-a")
    receipt = _receipt(raw_dir, "doc-a", b"version-one")
    extractor = RecordingExtractor()

    first = build_corpus_snapshot(
        (entry,),
        (receipt,),
        raw_dir,
        extractor,
        generated_at="2026-08-31T12:00:00+00:00",
    )
    second = build_corpus_snapshot(
        (entry,),
        (receipt,),
        raw_dir,
        extractor,
        generated_at="2026-09-01T12:00:00+00:00",
    )

    assert first.manifest["corpus_version"] == second.manifest["corpus_version"]
    assert first.changes.added == ("doc-a",)
    assert first.chunks[0]["document_sha256"] == receipt.sha256
    assert (
        first.chunks[0]["chunk_sha256"]
        == hashlib.sha256(str(first.chunks[0]["text"]).encode()).hexdigest()
    )
    document = first.manifest["documents"][0]
    assert document["final_url"] == receipt.final_url
    assert document["license_status"] == entry.license_status
    assert document["primary_theme"] == entry.primary_theme
    assert first.chunks[0]["primary_theme"] == entry.primary_theme


def test_unchanged_document_is_reused_and_metadata_is_refreshed(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    entry = _entry("doc-a")
    receipt = _receipt(raw_dir, "doc-a", b"same-content")
    first_extractor = RecordingExtractor()
    first = build_corpus_snapshot((entry,), (receipt,), raw_dir, first_extractor)
    chunks_path, manifest_path = _publish(first, processed_dir)
    previous_ids = tuple(row["chunk_id"] for row in first.chunks)

    updated_entry = replace(entry, metadata=replace(entry.metadata, title="Título corrigido"))
    second_extractor = RecordingExtractor()
    second = build_corpus_snapshot(
        (updated_entry,),
        (receipt,),
        raw_dir,
        second_extractor,
        previous_manifest_path=manifest_path,
        previous_chunks_path=chunks_path,
    )

    assert second_extractor.calls == []
    assert second.changes.metadata_updated == ("doc-a",)
    assert tuple(row["chunk_id"] for row in second.chunks) == previous_ids
    assert {row["document_title"] for row in second.chunks} == {"Título corrigido"}
    assert second.manifest["corpus_version"] != first.manifest["corpus_version"]


def test_changed_document_is_reprocessed_and_removed_document_disappears(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    entries = (_entry("doc-a"), _entry("doc-b"))
    receipts = (
        _receipt(raw_dir, "doc-a", b"version-one"),
        _receipt(raw_dir, "doc-b", b"document-b"),
    )
    first = build_corpus_snapshot(entries, receipts, raw_dir, RecordingExtractor())
    chunks_path, manifest_path = _publish(first, processed_dir)

    changed_receipt = _receipt(raw_dir, "doc-a", b"version-two")
    extractor = RecordingExtractor()
    second = build_corpus_snapshot(
        (entries[0],),
        (changed_receipt,),
        raw_dir,
        extractor,
        previous_manifest_path=manifest_path,
        previous_chunks_path=chunks_path,
    )

    assert extractor.calls == ["doc-a"]
    assert second.changes.reprocessed == ("doc-a",)
    assert second.changes.removed == ("doc-b",)
    assert {row["document_id"] for row in second.chunks} == {"doc-a"}


def test_tampered_previous_chunks_are_rejected(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    entry = _entry("doc-a")
    receipt = _receipt(raw_dir, "doc-a", b"content")
    first = build_corpus_snapshot((entry,), (receipt,), raw_dir, RecordingExtractor())
    chunks_path, manifest_path = _publish(first, processed_dir)
    chunks_path.write_text(json.dumps({"document_id": "doc-a", "text": "alterado"}) + "\n")

    with pytest.raises(CorpusVersioningError, match="divergem do manifesto"):
        build_corpus_snapshot(
            (entry,),
            (receipt,),
            raw_dir,
            RecordingExtractor(),
            previous_manifest_path=manifest_path,
            previous_chunks_path=chunks_path,
        )


def test_tampered_manifest_identity_is_rejected(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    entry = _entry("doc-a")
    receipt = _receipt(raw_dir, "doc-a", b"content")
    first = build_corpus_snapshot((entry,), (receipt,), raw_dir, RecordingExtractor())
    chunks_path, manifest_path = _publish(first, processed_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["documents"][0]["build_key"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(CorpusVersioningError, match="identidade"):
        build_corpus_snapshot(
            (entry,),
            (receipt,),
            raw_dir,
            RecordingExtractor(),
            previous_manifest_path=manifest_path,
            previous_chunks_path=chunks_path,
        )


def test_published_corpus_round_trip(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    entry = _entry("doc-a")
    receipt = _receipt(raw_dir, "doc-a", b"content")
    snapshot = build_corpus_snapshot((entry,), (receipt,), raw_dir, RecordingExtractor())
    chunks_path, manifest_path = _publish(snapshot, processed_dir)

    loaded = load_published_corpus(
        manifest_path=manifest_path,
        chunks_path=chunks_path,
        report_path=processed_dir / "validation_report.json",
    )

    assert loaded.manifest["corpus_version"] == snapshot.manifest["corpus_version"]
    assert loaded.chunks == snapshot.chunks
    assert loaded.changes.added == ("doc-a",)


def test_validated_document_without_receipt_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(CorpusVersioningError, match="sem recibo"):
        build_corpus_snapshot((_entry("doc-a"),), (), tmp_path, RecordingExtractor())
