from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from immunocheck.ingestion.catalog import CatalogEntry


class DownloadError(RuntimeError):
    """Indica falha ou violação de política durante download do corpus."""


SAFE_DOCUMENT_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,99}$")
DEFAULT_ALLOWED_DOMAINS = ("gov.br", "paho.org")


class ReadableResponse(Protocol):
    def read(self, size: int) -> bytes: ...


@dataclass(frozen=True, slots=True)
class DownloadReceipt:
    document_id: str
    relative_path: str
    sha256: str
    size_bytes: int
    content_type: str
    source_url: str
    final_url: str
    downloaded_at: str


def download_catalog_entry(
    entry: CatalogEntry,
    destination_dir: Path,
    *,
    max_bytes: int = 50 * 1024 * 1024,
    timeout_seconds: float = 30.0,
    allowed_domains: tuple[str, ...] = DEFAULT_ALLOWED_DOMAINS,
) -> DownloadReceipt:
    if not SAFE_DOCUMENT_ID.fullmatch(entry.metadata.document_id):
        raise DownloadError("document_id inseguro para uso como nome de arquivo.")
    _validate_url(entry.metadata.url, allowed_domains)
    if max_bytes <= 0:
        raise ValueError("max_bytes deve ser positivo.")

    request = Request(
        entry.metadata.url,
        headers={"User-Agent": "ImmunoCheck-TCC/0.1 (academic corpus collection)"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            final_url = response.geturl()
            _validate_url(final_url, allowed_domains)
            declared_size = response.headers.get("Content-Length")
            if declared_size and int(declared_size) > max_bytes:
                raise DownloadError("O documento excede o limite de download.")
            content_type = response.headers.get_content_type()
            content = _read_limited(response, max_bytes=max_bytes)
            _validate_content(entry.metadata.format, content_type, content)
    except DownloadError:
        raise
    except Exception as exc:
        raise DownloadError(f"Falha ao baixar {entry.metadata.document_id}.") from exc

    extension = ".pdf" if entry.metadata.format == "pdf" else ".html"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{entry.metadata.document_id}{extension}"
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(destination)

    return DownloadReceipt(
        document_id=entry.metadata.document_id,
        relative_path=destination.name,
        sha256=hashlib.sha256(content).hexdigest(),
        size_bytes=len(content),
        content_type=content_type,
        source_url=entry.metadata.url,
        final_url=final_url,
        downloaded_at=datetime.now(UTC).isoformat(),
    )


def write_receipts(receipts: tuple[DownloadReceipt, ...], path: Path) -> None:
    payload = [asdict(receipt) for receipt in receipts]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _read_limited(response: ReadableResponse, *, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(64 * 1024, max_bytes - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise DownloadError("O documento excede o limite de download.")
        chunks.append(chunk)
    return b"".join(chunks)


def _validate_content(expected_format: str, content_type: str, content: bytes) -> None:
    if not content:
        raise DownloadError("O servidor retornou um documento vazio.")

    if expected_format == "pdf":
        if not content.startswith(b"%PDF-"):
            raise DownloadError("O conteúdo recebido não possui assinatura de PDF.")
        if content_type not in {"application/pdf", "application/octet-stream"}:
            raise DownloadError(f"Tipo de conteúdo incompatível com PDF: {content_type}")
        return

    if expected_format == "html":
        if content.startswith(b"%PDF-"):
            raise DownloadError("O conteúdo recebido é PDF, mas o catálogo declara HTML.")
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise DownloadError(f"Tipo de conteúdo incompatível com HTML: {content_type}")
        return

    raise DownloadError(f"Formato de conteúdo não suportado: {expected_format}")


def _validate_url(url: str, allowed_domains: tuple[str, ...]) -> None:
    parsed = urlsplit(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme.lower() != "https" or not hostname:
        raise DownloadError("O corpus aceita apenas URLs HTTPS.")
    if parsed.username or parsed.password:
        raise DownloadError("URLs com credenciais não são aceitas.")
    if not any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowed_domains):
        raise DownloadError(f"Domínio não autorizado para o corpus: {hostname}")
