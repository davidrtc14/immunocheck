"""Extração do conteúdo principal de links com trafilatura (ADR-050).

A busca continua no `SafeWebFetcher` (HTTPS público, IP fixado, limites de tamanho e tempo). O
trafilatura só recebe o HTML já baixado; ele nunca acessa a rede. Se ele não achar conteúdo
principal, vale a extração por lista de tags de `web_content`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlsplit

import trafilatura

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.infrastructure.web_content import (
    SafeLinkTextExtractor,
    SafeWebFetcher,
    _decode_text,
    _extract_html_text,
    _normalize_text,
)

MINIMUM_USEFUL_CHARACTERS = 40
# Redes que só entregam a página de login a um cliente sem sessão.
LOGIN_WALLED_DOMAINS = (
    "instagram.com",
    "facebook.com",
    "fb.watch",
    "x.com",
    "twitter.com",
    "tiktok.com",
    "kwai.com",
    "threads.net",
    "whatsapp.com",
    "youtube.com",
    "youtu.be",
)
LOGIN_WALL_MESSAGE = (
    "Links de redes sociais exigem login e não podem ser lidos pelo protótipo. "
    "Envie o texto da publicação ou uma captura de tela."
)


@dataclass(frozen=True, slots=True)
class MainContentLinkExtractor:
    fetcher: SafeWebFetcher = field(default_factory=SafeWebFetcher)
    maximum_text_characters: int = 50_000
    maximum_pdf_pages: int = 100

    def extract(self, url: str) -> str:
        if is_login_walled(url):
            raise ContentExtractionError(LOGIN_WALL_MESSAGE)
        resource = self.fetcher.fetch(url)
        media_type = resource.content_type.split(";", maxsplit=1)[0].strip().lower()
        if media_type == "application/pdf":
            text = SafeLinkTextExtractor(
                fetcher=self.fetcher,
                maximum_text_characters=self.maximum_text_characters,
                maximum_pdf_pages=self.maximum_pdf_pages,
            )._extract_pdf(resource.body)
        else:
            decoded = _decode_text(resource.body, resource.content_type)
            text = main_html_text(decoded) if "html" in media_type else _normalize_text(decoded)
        if len(text) < MINIMUM_USEFUL_CHARACTERS:
            raise ContentExtractionError("O link não contém texto útil suficiente.")
        if len(text) > self.maximum_text_characters:
            raise ContentExtractionError(
                "O link excede 50 mil caracteres úteis; envie o trecho principal."
            )
        return text


def main_html_text(html: str) -> str:
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        include_links=False,
        include_images=False,
        favor_precision=True,
        deduplicate=True,
    )
    main = _normalize_text(extracted or "")
    if len(main) >= MINIMUM_USEFUL_CHARACTERS:
        return main
    return _extract_html_text(html)


def is_login_walled(url: str) -> bool:
    hostname = (urlsplit(url).hostname or "").lower()
    return any(hostname == domain or hostname.endswith("." + domain) for domain in
               LOGIN_WALLED_DOMAINS)
