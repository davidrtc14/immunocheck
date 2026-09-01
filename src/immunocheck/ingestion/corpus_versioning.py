from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from immunocheck.ingestion.catalog import CatalogEntry
from immunocheck.ingestion.chunker import chunk_document
from immunocheck.ingestion.downloader import DownloadReceipt
from immunocheck.ingestion.models import ExtractedDocument, TextChunk

CORPUS_MANIFEST_SCHEMA_VERSION = 2
SUPPORTED_CORPUS_MANIFEST_SCHEMA_VERSIONS = {1, CORPUS_MANIFEST_SCHEMA_VERSION}
CHUNK_SCHEMA_VERSION = 2
CHUNKER_VERSION = "1"
EXTRACTOR_VERSION = "1"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CorpusVersioningError(RuntimeError):
    """Indica que uma versão do corpus não pode ser construída ou validada."""


@dataclass(frozen=True, slots=True)
class BuildSettings:
    max_chars: int = 1_200
    overlap_chars: int = 200
    chunker_version: str = CHUNKER_VERSION
    extractor_version: str = EXTRACTOR_VERSION

    def __post_init__(self) -> None:
        if self.max_chars <= 0:
            raise ValueError("max_chars deve ser positivo.")
        if self.overlap_chars < 0 or self.overlap_chars >= self.max_chars:
            raise ValueError("overlap_chars deve ser não negativo e menor que max_chars.")


@dataclass(frozen=True, slots=True)
class CorpusChanges:
    added: tuple[str, ...]
    reprocessed: tuple[str, ...]
    metadata_updated: tuple[str, ...]
    reused: tuple[str, ...]
    removed: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CorpusSnapshot:
    manifest: dict[str, object]
    chunks: tuple[dict[str, object], ...]
    report: tuple[dict[str, object], ...]
    changes: CorpusChanges


DocumentExtractor = Callable[[Path, CatalogEntry], ExtractedDocument]


def load_download_receipts(path: Path) -> tuple[DownloadReceipt, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorpusVersioningError("Não foi possível ler os recibos de download.") from exc
    if not isinstance(payload, list):
        raise CorpusVersioningError("Os recibos de download devem formar uma lista JSON.")

    receipts: list[DownloadReceipt] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise CorpusVersioningError(f"Recibo inválido na posição {index}.")
        receipt = DownloadReceipt(
            document_id=_required_text(item, "document_id", index),
            relative_path=_required_text(item, "relative_path", index),
            sha256=_required_text(item, "sha256", index),
            size_bytes=_required_int(item, "size_bytes", index),
            content_type=_required_text(item, "content_type", index),
            source_url=_required_text(item, "source_url", index),
            final_url=_required_text(item, "final_url", index),
            downloaded_at=_required_text(item, "downloaded_at", index),
        )
        if not SHA256_PATTERN.fullmatch(receipt.sha256):
            raise CorpusVersioningError(f"SHA-256 inválido no recibo de {receipt.document_id}.")
        relative_path = Path(receipt.relative_path)
        if relative_path.is_absolute() or len(relative_path.parts) != 1:
            raise CorpusVersioningError(
                f"Caminho relativo inseguro no recibo de {receipt.document_id}."
            )
        receipts.append(receipt)

    ids = [receipt.document_id for receipt in receipts]
    if len(ids) != len(set(ids)):
        raise CorpusVersioningError("Há recibos duplicados para o mesmo document_id.")
    return tuple(receipts)


def build_corpus_snapshot(
    entries: Iterable[CatalogEntry],
    receipts: Iterable[DownloadReceipt],
    raw_dir: Path,
    extractor: DocumentExtractor,
    *,
    settings: BuildSettings | None = None,
    previous_manifest_path: Path | None = None,
    previous_chunks_path: Path | None = None,
    generated_at: str | None = None,
) -> CorpusSnapshot:
    settings = settings or BuildSettings()
    all_entries = tuple(entries)
    all_receipts = tuple(receipts)
    approved_entries = {
        entry.metadata.document_id: entry for entry in all_entries if entry.status == "validated"
    }
    if not approved_entries:
        raise CorpusVersioningError("O corpus precisa conter ao menos um documento validado.")
    receipt_by_id = {receipt.document_id: receipt for receipt in all_receipts}
    if len(receipt_by_id) != len(all_receipts):
        raise CorpusVersioningError("Há recibos duplicados para o mesmo document_id.")
    missing = sorted(set(approved_entries).difference(receipt_by_id))
    if missing:
        raise CorpusVersioningError(
            "Documentos validados sem recibo de download: " + ", ".join(missing)
        )
    catalog_ids = {entry.metadata.document_id for entry in all_entries}
    unknown = sorted(set(receipt_by_id).difference(catalog_ids))
    if unknown:
        raise CorpusVersioningError("Recibos sem entrada no catálogo: " + ", ".join(unknown))

    previous_manifest, previous_chunks = _load_previous_snapshot(
        previous_manifest_path, previous_chunks_path
    )
    previous_documents = {
        str(item["document_id"]): item for item in _manifest_documents(previous_manifest)
    }
    previous_by_document = _group_chunks(previous_chunks)

    chunk_rows: list[dict[str, object]] = []
    document_records: list[dict[str, object]] = []
    report: list[dict[str, object]] = []
    added: list[str] = []
    reprocessed: list[str] = []
    metadata_updated: list[str] = []
    reused: list[str] = []

    for document_id in sorted(approved_entries):
        entry = approved_entries[document_id]
        receipt = receipt_by_id[document_id]
        raw_path = raw_dir / receipt.relative_path
        _verify_download(raw_path, receipt)
        build_key = _document_build_key(document_id, receipt, entry, settings)
        metadata_sha256 = _metadata_sha256(entry, receipt)
        previous_record = previous_documents.get(document_id)
        can_reuse = (
            previous_record is not None
            and previous_record.get("build_key") == build_key
            and document_id in previous_by_document
        )

        if can_reuse:
            previous_rows = previous_by_document[document_id]
            _validate_reused_chunks(previous_rows, previous_record)
            rows = tuple(_refresh_chunk_provenance(row, entry, receipt) for row in previous_rows)
            pages = _required_positive_manifest_int(previous_record, "page_count", document_id)
            characters = _required_positive_manifest_int(
                previous_record, "character_count", document_id
            )
            warnings = _manifest_warnings(previous_record, document_id)
            if previous_record.get("metadata_sha256") == metadata_sha256:
                reused.append(document_id)
                action = "reused"
            else:
                metadata_updated.append(document_id)
                action = "metadata_updated"
        else:
            try:
                document = extractor(raw_path, entry)
                chunks = chunk_document(
                    document,
                    max_chars=settings.max_chars,
                    overlap_chars=settings.overlap_chars,
                )
            except Exception as exc:
                raise CorpusVersioningError(
                    f"Falha ao processar o documento {document_id}: {type(exc).__name__}: {exc}"
                ) from exc
            if not chunks:
                raise CorpusVersioningError(f"A segmentação de {document_id} não produziu trechos.")
            rows = tuple(_serialize_chunk(chunk, entry, receipt) for chunk in chunks)
            pages = len(document.pages)
            characters = sum(len(page.text) for page in document.pages)
            warnings = document.extraction_warnings
            if previous_record is None:
                added.append(document_id)
                action = "added"
            else:
                reprocessed.append(document_id)
                action = "reprocessed"

        record = _document_record(
            entry,
            receipt,
            settings,
            build_key=build_key,
            metadata_sha256=metadata_sha256,
            chunks=rows,
            pages=pages,
            characters=characters,
            warnings=warnings,
        )
        document_records.append(record)
        chunk_rows.extend(rows)
        report.append(
            {
                "document_id": document_id,
                "status": "validated",
                "action": action,
                "pages": pages,
                "characters": characters,
                "chunks": len(rows),
                "warnings": list(warnings),
            }
        )

    removed = sorted(set(previous_documents).difference(approved_entries))
    changes = CorpusChanges(
        added=tuple(added),
        reprocessed=tuple(reprocessed),
        metadata_updated=tuple(metadata_updated),
        reused=tuple(reused),
        removed=tuple(removed),
    )
    chunks_bytes = _jsonl_bytes(chunk_rows)
    chunks_sha256 = _sha256(chunks_bytes)
    stable_manifest = {
        "schema_version": CORPUS_MANIFEST_SCHEMA_VERSION,
        "build": asdict(settings),
        "chunks_sha256": chunks_sha256,
        "document_count": len(document_records),
        "chunk_count": len(chunk_rows),
        "documents": document_records,
    }
    corpus_version = _corpus_version(stable_manifest)
    manifest = {
        **stable_manifest,
        "corpus_version": corpus_version,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "changes": asdict(changes),
        "previous_corpus_version": (
            previous_manifest.get("corpus_version") if previous_manifest is not None else None
        ),
    }
    return CorpusSnapshot(
        manifest=manifest,
        chunks=tuple(chunk_rows),
        report=tuple(report),
        changes=changes,
    )


def publish_corpus_snapshot(
    snapshot: CorpusSnapshot,
    *,
    chunks_path: Path,
    report_path: Path,
    manifest_path: Path,
) -> None:
    chunks_bytes = _jsonl_bytes(snapshot.chunks)
    if _sha256(chunks_bytes) != snapshot.manifest["chunks_sha256"]:
        raise CorpusVersioningError("O hash dos chunks diverge do manifesto antes da publicação.")
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(chunks_path, chunks_bytes)
    _atomic_write(
        report_path,
        json.dumps(snapshot.report, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )
    # O manifesto funciona como marcador de commit e, por isso, é publicado por último.
    _atomic_write(
        manifest_path,
        json.dumps(snapshot.manifest, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
    )


def load_published_corpus(
    *,
    manifest_path: Path,
    chunks_path: Path,
    report_path: Path | None = None,
) -> CorpusSnapshot:
    manifest, chunks = _load_previous_snapshot(manifest_path, chunks_path)
    if manifest is None:
        raise CorpusVersioningError("O manifesto publicado está ausente.")
    report: tuple[dict[str, object], ...] = ()
    if report_path is not None and report_path.exists():
        try:
            raw_report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CorpusVersioningError("O relatório publicado está inválido.") from exc
        if not isinstance(raw_report, list) or not all(
            isinstance(item, dict) for item in raw_report
        ):
            raise CorpusVersioningError("O relatório publicado está inválido.")
        report = tuple(raw_report)
    changes = _parse_manifest_changes(manifest.get("changes"))
    return CorpusSnapshot(manifest=manifest, chunks=chunks, report=report, changes=changes)


def _load_previous_snapshot(
    manifest_path: Path | None,
    chunks_path: Path | None,
) -> tuple[dict[str, object] | None, tuple[dict[str, object], ...]]:
    if manifest_path is None or not manifest_path.exists():
        return None, ()
    if chunks_path is None or not chunks_path.exists():
        raise CorpusVersioningError("O manifesto anterior existe, mas os chunks estão ausentes.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise TypeError
        if manifest.get("schema_version") not in SUPPORTED_CORPUS_MANIFEST_SCHEMA_VERSIONS:
            raise CorpusVersioningError("Versão de schema do manifesto não suportada.")
        chunks_bytes = chunks_path.read_bytes()
        if manifest.get("chunks_sha256") != _sha256(chunks_bytes):
            raise CorpusVersioningError("Os chunks anteriores divergem do manifesto.")
        stable_manifest = {
            key: manifest.get(key)
            for key in (
                "schema_version",
                "build",
                "chunks_sha256",
                "document_count",
                "chunk_count",
                "documents",
            )
        }
        if manifest.get("corpus_version") != _corpus_version(stable_manifest):
            raise CorpusVersioningError("A identidade do manifesto anterior é inválida.")
        chunks = tuple(
            json.loads(line) for line in chunks_bytes.decode("utf-8").splitlines() if line.strip()
        )
    except CorpusVersioningError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise CorpusVersioningError("A versão anterior do corpus está inválida.") from exc
    if not all(isinstance(row, dict) for row in chunks):
        raise CorpusVersioningError("A versão anterior contém chunk inválido.")
    if manifest.get("chunk_count") != len(chunks):
        raise CorpusVersioningError("A contagem de chunks diverge do manifesto anterior.")
    if manifest.get("document_count") != len(_manifest_documents(manifest)):
        raise CorpusVersioningError("A contagem de documentos diverge do manifesto anterior.")
    return manifest, chunks


def _serialize_chunk(
    chunk: TextChunk,
    entry: CatalogEntry,
    receipt: DownloadReceipt,
) -> dict[str, object]:
    return {
        **asdict(chunk),
        "schema_version": CHUNK_SCHEMA_VERSION,
        "chunk_sha256": _sha256(chunk.text.encode("utf-8")),
        "document_sha256": receipt.sha256,
        "document_type": entry.metadata.document_type,
        "primary_theme": entry.primary_theme,
        "format": entry.metadata.format,
        "access_date": entry.access_date,
        "downloaded_at": receipt.downloaded_at,
        "final_url": receipt.final_url,
        "license_status": entry.license_status,
    }


def _refresh_chunk_provenance(
    row: Mapping[str, object],
    entry: CatalogEntry,
    receipt: DownloadReceipt,
) -> dict[str, object]:
    refreshed = dict(row)
    refreshed.update(
        {
            "source": entry.metadata.source,
            "document_title": entry.metadata.title,
            "url": entry.metadata.url,
            "publication_date": entry.metadata.publication_date,
            "schema_version": CHUNK_SCHEMA_VERSION,
            "document_sha256": receipt.sha256,
            "document_type": entry.metadata.document_type,
            "primary_theme": entry.primary_theme,
            "format": entry.metadata.format,
            "access_date": entry.access_date,
            "downloaded_at": receipt.downloaded_at,
            "final_url": receipt.final_url,
            "license_status": entry.license_status,
        }
    )
    text = refreshed.get("text")
    if not isinstance(text, str) or not text:
        raise CorpusVersioningError("Um chunk reutilizado não possui texto válido.")
    refreshed["chunk_sha256"] = _sha256(text.encode("utf-8"))
    return refreshed


def _document_record(
    entry: CatalogEntry,
    receipt: DownloadReceipt,
    settings: BuildSettings,
    *,
    build_key: str,
    metadata_sha256: str,
    chunks: tuple[dict[str, object], ...],
    pages: int,
    characters: int,
    warnings: tuple[str, ...],
) -> dict[str, object]:
    chunk_ids = [str(row["chunk_id"]) for row in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise CorpusVersioningError(f"Chunks duplicados no documento {entry.metadata.document_id}.")
    return {
        "document_id": entry.metadata.document_id,
        "title": entry.metadata.title,
        "source": entry.metadata.source,
        "document_type": entry.metadata.document_type,
        "primary_theme": entry.primary_theme,
        "publication_date": entry.metadata.publication_date,
        "access_date": entry.access_date,
        "url": entry.metadata.url,
        "final_url": receipt.final_url,
        "format": entry.metadata.format,
        "license_status": entry.license_status,
        "content_type": receipt.content_type,
        "relative_path": receipt.relative_path,
        "downloaded_at": receipt.downloaded_at,
        "content_sha256": receipt.sha256,
        "size_bytes": receipt.size_bytes,
        "metadata_sha256": metadata_sha256,
        "build_key": build_key,
        "build_settings": asdict(settings),
        "page_count": pages,
        "character_count": characters,
        "chunk_count": len(chunks),
        "chunk_ids": chunk_ids,
        "chunk_set_sha256": _sha256(_canonical_json_bytes(chunk_ids)),
        "extraction_warnings": list(warnings),
    }


def _validate_reused_chunks(
    rows: tuple[dict[str, object], ...], previous_record: Mapping[str, object]
) -> None:
    expected_ids = previous_record.get("chunk_ids")
    actual_ids = [row.get("chunk_id") for row in rows]
    if not isinstance(expected_ids, list) or actual_ids != expected_ids:
        raise CorpusVersioningError("Os chunks reutilizados divergem do manifesto anterior.")
    if previous_record.get("chunk_set_sha256") != _sha256(_canonical_json_bytes(expected_ids)):
        raise CorpusVersioningError("Os IDs de chunk divergem do manifesto anterior.")
    for row in rows:
        text = row.get("text")
        digest = row.get("chunk_sha256")
        if not isinstance(text, str) or digest != _sha256(text.encode("utf-8")):
            raise CorpusVersioningError(
                "Um chunk reutilizado falhou na verificação de integridade."
            )


def _document_build_key(
    document_id: str,
    receipt: DownloadReceipt,
    entry: CatalogEntry,
    settings: BuildSettings,
) -> str:
    payload = {
        "document_id": document_id,
        "content_sha256": receipt.sha256,
        "format": entry.metadata.format,
        "build": asdict(settings),
    }
    return _sha256(_canonical_json_bytes(payload))


def _metadata_sha256(entry: CatalogEntry, receipt: DownloadReceipt) -> str:
    payload = {
        "metadata": asdict(entry.metadata),
        "primary_theme": entry.primary_theme,
        "access_date": entry.access_date,
        "license_status": entry.license_status,
        "source_url": receipt.source_url,
        "final_url": receipt.final_url,
        "downloaded_at": receipt.downloaded_at,
    }
    return _sha256(_canonical_json_bytes(payload))


def _verify_download(path: Path, receipt: DownloadReceipt) -> None:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise CorpusVersioningError(f"Arquivo bruto ausente para {receipt.document_id}.") from exc
    if len(content) != receipt.size_bytes:
        raise CorpusVersioningError(f"Tamanho divergente do recibo para {path.name}.")
    if _sha256(content) != receipt.sha256:
        raise CorpusVersioningError(f"SHA-256 divergente do recibo para {path.name}.")


def _group_chunks(
    rows: tuple[dict[str, object], ...],
) -> dict[str, tuple[dict[str, object], ...]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        document_id = row.get("document_id")
        if not isinstance(document_id, str) or not document_id:
            raise CorpusVersioningError("Chunk anterior sem document_id válido.")
        grouped.setdefault(document_id, []).append(row)
    return {key: tuple(value) for key, value in grouped.items()}


def _manifest_documents(manifest: dict[str, object] | None) -> tuple[dict[str, object], ...]:
    if manifest is None:
        return ()
    documents = manifest.get("documents")
    if not isinstance(documents, list) or not all(isinstance(item, dict) for item in documents):
        raise CorpusVersioningError("A lista de documentos do manifesto está inválida.")
    return tuple(documents)


def _required_positive_manifest_int(
    record: Mapping[str, object], field: str, document_id: str
) -> int:
    value = record.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise CorpusVersioningError(f"{field} inválido no manifesto de {document_id}.")
    return value


def _manifest_warnings(record: Mapping[str, object], document_id: str) -> tuple[str, ...]:
    warnings = record.get("extraction_warnings")
    if not isinstance(warnings, list) or not all(isinstance(item, str) for item in warnings):
        raise CorpusVersioningError(f"Avisos inválidos no manifesto de {document_id}.")
    return tuple(warnings)


def _parse_manifest_changes(value: object) -> CorpusChanges:
    if not isinstance(value, dict):
        raise CorpusVersioningError("O resumo de mudanças do manifesto está inválido.")
    parsed: dict[str, tuple[str, ...]] = {}
    for field in ("added", "reprocessed", "metadata_updated", "reused", "removed"):
        items = value.get(field)
        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            raise CorpusVersioningError("O resumo de mudanças do manifesto está inválido.")
        parsed[field] = tuple(items)
    return CorpusChanges(**parsed)


def _required_text(item: Mapping[str, object], field: str, index: int) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value.strip():
        raise CorpusVersioningError(f"Campo {field} inválido no recibo {index}.")
    return value


def _required_int(item: Mapping[str, object], field: str, index: int) -> int:
    value = item.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise CorpusVersioningError(f"Campo {field} inválido no recibo {index}.")
    return value


def _jsonl_bytes(rows: Iterable[Mapping[str, object]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        for row in rows
    )


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _corpus_version(stable_manifest: Mapping[str, object]) -> str:
    return "sha256:" + _sha256(_canonical_json_bytes(stable_manifest))


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise CorpusVersioningError(f"Falha ao publicar {path.name}.") from exc
