from __future__ import annotations

import http.client
import ipaddress
import re
import socket
import ssl
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from io import BytesIO
from typing import Protocol
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from pypdf import PdfReader

from immunocheck.application.content_normalizer import ContentExtractionError

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/xhtml+xml",
    "text/html",
    "text/plain",
}
REDIRECT_STATUSES = {301, 302, 303, 307, 308}
REMOVABLE_TAGS = (
    "script",
    "style",
    "noscript",
    "nav",
    "footer",
    "header",
    "form",
    "aside",
    "svg",
    "template",
)
CHARSET_PATTERN = re.compile(r"charset\s*=\s*['\"]?([^;'\"\s]+)", re.IGNORECASE)


class HTTPResponseLike(Protocol):
    status: int

    def getheader(self, name: str, default: str | None = None) -> str | None: ...

    def read(self, amount: int = -1) -> bytes: ...

    def close(self) -> None: ...


class HTTPSConnectionLike(Protocol):
    def request(self, method: str, url: str, *, headers: dict[str, str]) -> None: ...

    def getresponse(self) -> HTTPResponseLike: ...

    def close(self) -> None: ...


Resolver = Callable[[str, int], tuple[str, ...]]
ConnectionFactory = Callable[[str, int, str, float], HTTPSConnectionLike]


@dataclass(frozen=True, slots=True)
class FetchedResource:
    final_url: str
    content_type: str
    body: bytes


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, hostname: str, port: int, resolved_ip: str, timeout: float) -> None:
        super().__init__(
            hostname,
            port=port,
            timeout=timeout,
            context=ssl.create_default_context(),
        )
        self._resolved_ip = resolved_ip

    def connect(self) -> None:
        raw_socket = socket.create_connection(
            (self._resolved_ip, self.port),
            timeout=self.timeout,
            source_address=self.source_address,
        )
        try:
            self.sock = self._context.wrap_socket(raw_socket, server_hostname=self.host)
        except Exception:
            raw_socket.close()
            raise


def _default_resolver(hostname: str, port: int) -> tuple[str, ...]:
    try:
        answers = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ContentExtractionError("Não foi possível resolver o endereço do link.") from exc
    addresses = tuple(dict.fromkeys(answer[4][0] for answer in answers))
    if not addresses:
        raise ContentExtractionError("O link não possui endereço de rede válido.")
    return addresses


def _default_connection_factory(
    hostname: str,
    port: int,
    resolved_ip: str,
    timeout: float,
) -> HTTPSConnectionLike:
    return _PinnedHTTPSConnection(hostname, port, resolved_ip, timeout)


@dataclass(frozen=True, slots=True)
class SafeWebFetcher:
    maximum_bytes: int = 5 * 1024 * 1024
    timeout_seconds: float = 10.0
    maximum_redirects: int = 3
    resolver: Resolver = _default_resolver
    connection_factory: ConnectionFactory = _default_connection_factory
    clock: Callable[[], float] = time.monotonic

    def fetch(self, url: str) -> FetchedResource:
        if self.maximum_bytes <= 0 or self.timeout_seconds <= 0:
            raise ValueError("Limites de download devem ser positivos.")
        if self.maximum_redirects < 0:
            raise ValueError("O limite de redirecionamentos não pode ser negativo.")
        deadline = self.clock() + self.timeout_seconds
        current_url = _canonical_public_https_url(url)

        for redirect_count in range(self.maximum_redirects + 1):
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise ContentExtractionError("O download do link excedeu 10 segundos.")
            parsed = urlsplit(current_url)
            hostname = parsed.hostname
            if hostname is None:
                raise ContentExtractionError("O link não possui host válido.")
            ascii_hostname = hostname.encode("idna").decode("ascii")
            addresses = self.resolver(ascii_hostname, 443)
            _require_global_addresses(addresses)
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise ContentExtractionError("O download do link excedeu 10 segundos.")
            connection = self.connection_factory(
                ascii_hostname,
                443,
                addresses[0],
                remaining,
            )
            response: HTTPResponseLike | None = None
            try:
                connection.request(
                    "GET",
                    _request_target(parsed.path, parsed.query),
                    headers={
                        "Accept": "text/html, application/xhtml+xml, text/plain, application/pdf",
                        "Accept-Encoding": "identity",
                        "User-Agent": "ImmunoCheck-TCC/0.1 (academic fact checking)",
                    },
                )
                response = connection.getresponse()
                if response.status in REDIRECT_STATUSES:
                    if redirect_count >= self.maximum_redirects:
                        raise ContentExtractionError("O link excedeu três redirecionamentos.")
                    location = response.getheader("Location")
                    if not location:
                        raise ContentExtractionError("O servidor retornou redirecionamento inválido.")
                    current_url = _canonical_public_https_url(urljoin(current_url, location))
                    continue
                if not 200 <= response.status < 300:
                    raise ContentExtractionError("O servidor recusou o download do conteúdo.")
                content_encoding = (response.getheader("Content-Encoding") or "identity").lower()
                if content_encoding not in {"", "identity"}:
                    raise ContentExtractionError("O servidor enviou compressão não aceita.")
                declared_length = response.getheader("Content-Length")
                if declared_length is not None:
                    try:
                        numeric_length = int(declared_length)
                        if numeric_length < 0:
                            raise ValueError
                        if numeric_length > self.maximum_bytes:
                            raise ContentExtractionError("O link excede o limite de 5 MB.")
                    except ValueError as exc:
                        raise ContentExtractionError("O servidor informou tamanho inválido.") from exc
                raw_content_type = response.getheader("Content-Type") or ""
                content_type = raw_content_type.split(";", maxsplit=1)[0].strip().lower()
                if content_type not in ALLOWED_CONTENT_TYPES:
                    raise ContentExtractionError("O tipo de conteúdo do link não é aceito.")
                body = _read_limited(response, self.maximum_bytes)
                _validate_signature(content_type, body)
                return FetchedResource(
                    final_url=current_url,
                    content_type=raw_content_type,
                    body=body,
                )
            except ContentExtractionError:
                raise
            except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
                raise ContentExtractionError("Não foi possível baixar o link com segurança.") from exc
            finally:
                if response is not None:
                    response.close()
                connection.close()
        raise ContentExtractionError("O link excedeu o limite de redirecionamentos.")


@dataclass(frozen=True, slots=True)
class SafeLinkTextExtractor:
    fetcher: SafeWebFetcher = field(default_factory=SafeWebFetcher)
    maximum_text_characters: int = 50_000
    maximum_pdf_pages: int = 100

    def extract(self, url: str) -> str:
        resource = self.fetcher.fetch(url)
        media_type = resource.content_type.split(";", maxsplit=1)[0].strip().lower()
        if media_type == "application/pdf":
            text = self._extract_pdf(resource.body)
        else:
            decoded = _decode_text(resource.body, resource.content_type)
            text = _extract_html_text(decoded) if "html" in media_type else _normalize_text(decoded)
        if len(text) < 40:
            raise ContentExtractionError("O link não contém texto útil suficiente.")
        if len(text) > self.maximum_text_characters:
            raise ContentExtractionError(
                "O link excede 50 mil caracteres úteis; envie o trecho principal."
            )
        return text

    def _extract_pdf(self, body: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(body))
            if len(reader.pages) > self.maximum_pdf_pages:
                raise ContentExtractionError("O PDF excede o limite de 100 páginas.")
            pages: list[str] = []
            for page in reader.pages:
                page_text = _normalize_text(page.extract_text() or "")
                if page_text:
                    pages.append(page_text)
                if sum(len(item) for item in pages) > self.maximum_text_characters:
                    raise ContentExtractionError(
                        "O PDF excede 50 mil caracteres úteis; envie o trecho principal."
                    )
        except ContentExtractionError:
            raise
        except Exception as exc:
            raise ContentExtractionError("Não foi possível extrair texto do PDF.") from exc
        if not pages:
            raise ContentExtractionError("O PDF não possui texto selecionável.")
        return "\n".join(pages)


def _canonical_public_https_url(url: str) -> str:
    if len(url) > 2_048:
        raise ContentExtractionError("A URL excede o limite permitido.")
    parsed = urlsplit(url)
    hostname = parsed.hostname
    if parsed.scheme.lower() != "https" or not hostname:
        raise ContentExtractionError("Apenas URLs HTTPS públicas são aceitas.")
    if parsed.username or parsed.password:
        raise ContentExtractionError("URLs com credenciais não são aceitas.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ContentExtractionError("A URL contém uma porta inválida.") from exc
    if port not in {None, 443}:
        raise ContentExtractionError("Apenas a porta HTTPS padrão é aceita.")
    try:
        ascii_hostname = hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise ContentExtractionError("O host do link não possui codificação válida.") from exc
    if not ascii_hostname or ascii_hostname == "localhost":
        raise ContentExtractionError("O host do link não é público.")
    netloc = ascii_hostname if port is None else f"{ascii_hostname}:{port}"
    return urlunsplit(("https", netloc, parsed.path or "/", parsed.query, ""))


def _require_global_addresses(addresses: tuple[str, ...]) -> None:
    try:
        parsed_addresses = tuple(ipaddress.ip_address(address) for address in addresses)
    except ValueError as exc:
        raise ContentExtractionError("O DNS retornou um endereço inválido.") from exc
    if not parsed_addresses or any(not address.is_global for address in parsed_addresses):
        raise ContentExtractionError("O link aponta para uma rede privada ou não pública.")


def _request_target(path: str, query: str) -> str:
    safe_path = quote(path or "/", safe="/%:@!$&'()*+,;=-._~")
    if not query:
        return safe_path
    return f"{safe_path}?{quote(query, safe='=&?/:;+,%@-._~')}"


def _read_limited(response: HTTPResponseLike, maximum_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(64 * 1024, maximum_bytes - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > maximum_bytes:
            raise ContentExtractionError("O link excede o limite de 5 MB.")
        chunks.append(chunk)
    if not chunks:
        raise ContentExtractionError("O servidor retornou conteúdo vazio.")
    return b"".join(chunks)


def _validate_signature(content_type: str, body: bytes) -> None:
    is_pdf = body.startswith(b"%PDF-")
    if content_type == "application/pdf" and not is_pdf:
        raise ContentExtractionError("O conteúdo não possui assinatura válida de PDF.")
    if content_type != "application/pdf" and is_pdf:
        raise ContentExtractionError("O tipo declarado não corresponde ao conteúdo recebido.")


def _decode_text(body: bytes, content_type: str) -> str:
    match = CHARSET_PATTERN.search(content_type)
    charset = match.group(1) if match else "utf-8"
    try:
        return body.decode(charset)
    except (LookupError, UnicodeDecodeError) as exc:
        raise ContentExtractionError("A codificação textual do link não é válida.") from exc


def _extract_html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(REMOVABLE_TAGS):
        element.decompose()
    content = soup.find("main") or soup.find("article") or soup.body
    if content is None:
        raise ContentExtractionError("A página não possui área textual reconhecível.")
    title = _normalize_text(soup.title.get_text(" ") if soup.title else "")
    body = _normalize_text(content.get_text("\n"))
    return "\n".join(part for part in (title, body) if part)


def _normalize_text(text: str) -> str:
    lines = (" ".join(line.replace("\x00", "").split()) for line in text.splitlines())
    return "\n".join(line for line in lines if line)
