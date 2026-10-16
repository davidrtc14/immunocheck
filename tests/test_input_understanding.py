from __future__ import annotations

from dataclasses import dataclass

import pytest

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.application.input_cleaning import (
    clean_forwarded_text,
    join_wrapped_lines,
    split_message_link,
    strip_interface_lines,
    strip_symbols,
)
from immunocheck.application.input_understanding import UnderstandingNormalizer, route_message
from immunocheck.application.passage_selection import select_claim_passages, topic_score
from immunocheck.domain.models import ContentKind, ContentSubmission
from immunocheck.infrastructure.main_content import (
    LOGIN_WALL_MESSAGE,
    MainContentLinkExtractor,
    is_login_walled,
    main_html_text,
)
from immunocheck.infrastructure.web_content import FetchedResource
from immunocheck.telegram import legacy_route_message

CLAIM = "A vacina contra o sarampo não causa autismo em 99% das crianças."


# --------------------------------------------------------------------------- limpeza


def test_forwarded_text_loses_emoji_markers_and_calls_to_action() -> None:
    raw = f"⚠️🚨 Encaminhada com frequência 🚨⚠️\n{CLAIM} 😱😱\nREPASSEM PARA TODOS OS GRUPOS!!! 🙏"
    assert clean_forwarded_text(raw) == CLAIM


def test_shouting_is_softened_but_acronyms_numbers_and_negations_survive() -> None:
    cleaned = clean_forwarded_text("ATENÇÃO!!! A VACINA DO HPV NÃO PROTEGE 90% DAS MENINAS DO SUS!!!")
    assert cleaned == "A vacina do HPV não protege 90% das meninas do SUS!"


def test_cleaning_keeps_words_that_only_look_like_markers() -> None:
    claim = "O paciente foi encaminhado ao posto e compartilhar seringas transmite hepatite."
    assert clean_forwarded_text(claim) == claim


def test_strip_symbols_keeps_degrees_and_ordinals() -> None:
    assert strip_symbols("Febre de 38°C na 2ª dose 💉") == "Febre de 38°C na 2ª dose "
    assert strip_symbols("eﬁcácia") == "eficácia"


def test_interface_lines_are_removed_and_wrapped_lines_joined() -> None:
    ocr = (
        "8:37 53%\nAmigos do Bairro\nonline\nEncaminhada com frequência\n"
        "A vacina contra o sarampo não causa\nautismo em 99% das crianças. 8:36\n"
        "4,9 mil comentários 9,9 mil compartilhamentos\nMensaderm"
    )
    assert strip_interface_lines(ocr) == f"Amigos do Bairro\n{CLAIM}"


def test_garbled_forward_marker_is_removed_from_line_start() -> None:
    assert strip_interface_lines(f"Emeenennada com frequentes {CLAIM}") == CLAIM


def test_join_wrapped_lines_merges_hyphenation_and_keeps_new_elements() -> None:
    assert join_wrapped_lines(["A vaci-", "nação protege", "Portal Alerta"]) == (
        "A vacinação protege\nPortal Alerta"
    )


def test_split_message_link_separates_comment_and_trailing_punctuation() -> None:
    assert split_message_link("Isso procede? https://ex.org/a/b.") == (
        "https://ex.org/a/b",
        "Isso procede?",
    )
    assert split_message_link("sem link") == (None, "sem link")


# --------------------------------------------------------------------------- roteamento


def test_route_message_turns_commented_https_link_into_link() -> None:
    routed = route_message("Recebi no grupo, é verdade? https://ex.org/materia")
    assert routed.kind is ContentKind.LINK
    assert routed.url == "https://ex.org/materia"
    assert routed.text == "Recebi no grupo, é verdade?"
    assert route_message("https://ex.org/materia").text is None


def test_route_message_keeps_plain_and_insecure_links_as_text() -> None:
    assert route_message(CLAIM).kind is ContentKind.TEXT
    assert route_message(f"{CLAIM} http://ex.org").kind is ContentKind.TEXT


def test_legacy_route_only_accepts_standalone_urls() -> None:
    assert legacy_route_message("https://ex.org/a").kind is ContentKind.LINK
    assert legacy_route_message("veja https://ex.org/a").kind is ContentKind.TEXT


# --------------------------------------------------------------------------- seleção de trechos


def test_long_text_keeps_title_and_topic_paragraphs() -> None:
    filler = "\n".join("A feira de artesanato reúne expositores do bairro." for _ in range(200))
    text = f"Resumo da semana\n{filler}\n{CLAIM}\nOutra notícia sobre o trânsito."
    selected, reduced = select_claim_passages(text, budget=500)
    assert reduced
    assert selected == f"Resumo da semana\n{CLAIM}"


def test_short_text_and_off_topic_text() -> None:
    assert select_claim_passages(CLAIM) == (CLAIM, False)
    off_topic = "Notícia\n" + "texto neutro " * 100
    selected, reduced = select_claim_passages(off_topic, budget=100)
    assert reduced and len(selected) <= 100
    assert topic_score("Tríplice viral e febre amarela") == 3


# --------------------------------------------------------------------------- normalizador


@dataclass
class FakeReading:
    text: str
    mean_confidence: float


@dataclass
class FakeReader:
    reading: FakeReading | None

    def read(self, submission):
        if self.reading is None:
            raise ContentExtractionError("ilegível")
        return self.reading


@dataclass
class FakeLinks:
    pages: dict[str, str]

    def extract(self, url: str) -> str:
        if url not in self.pages:
            raise ContentExtractionError("inacessível")
        return self.pages[url]


@dataclass
class FakeVision:
    text: str
    calls: int = 0

    def transcribe(self, submission):
        self.calls += 1
        return self.text


IMAGE = ContentSubmission(kind=ContentKind.IMAGE, data=b"x", media_type="image/png")


def _normalizer(reading=None, pages=None, vision=None) -> UnderstandingNormalizer:
    return UnderstandingNormalizer(
        image_reader=FakeReader(reading), link_extractor=FakeLinks(pages or {}), vision=vision
    )


def test_text_is_cleaned_to_one_line() -> None:
    raw = f"🚨 Encaminhada com frequência\n{CLAIM}\nCompartilhem!"
    result = _normalizer().normalize(ContentSubmission(kind=ContentKind.TEXT, text=raw))
    assert result == CLAIM
    with pytest.raises(ContentExtractionError):
        _normalizer().normalize(ContentSubmission(kind=ContentKind.TEXT, text="🙏🙏"))


def test_image_text_drops_interface_and_adds_caption() -> None:
    normalizer = _normalizer(FakeReading(f"10:42\n{CLAIM}", 90.0))
    assert normalizer.normalize(IMAGE) == CLAIM
    with_caption = ContentSubmission(
        kind=ContentKind.IMAGE, text="Isso é verdade??", data=b"x", media_type="image/png"
    )
    assert normalizer.normalize(with_caption) == (
        f"Legenda enviada com a imagem: Isso é verdade?\n\nTexto da imagem:\n{CLAIM}"
    )


def test_vision_is_used_only_for_failed_or_low_confidence_ocr() -> None:
    vision = FakeVision(f"Encaminhada com frequência\n{CLAIM}")
    assert _normalizer(FakeReading(CLAIM, 95.0), vision=vision).normalize(IMAGE) == CLAIM
    assert vision.calls == 0
    assert _normalizer(FakeReading("v4c1na", 30.0), vision=vision).normalize(IMAGE) == CLAIM
    assert _normalizer(None, vision=vision).normalize(IMAGE) == CLAIM
    assert vision.calls == 2


def test_unreadable_image_without_vision_falls_back_to_caption_or_fails() -> None:
    with pytest.raises(ContentExtractionError):
        _normalizer(None).normalize(IMAGE)
    captioned = ContentSubmission(kind=ContentKind.IMAGE, text=CLAIM, data=b"x",
                                  media_type="image/png")
    assert _normalizer(None).normalize(captioned) == CLAIM


def test_link_with_comment_and_unreachable_link_fallback() -> None:
    pages = {"https://ex.org/a": f"Título\n{CLAIM}"}
    commented = ContentSubmission(kind=ContentKind.LINK, url="https://ex.org/a", text="É verdade?")
    assert _normalizer(pages=pages).normalize(commented) == (
        f"Mensagem de quem enviou: É verdade?\n\nConteúdo do link:\nTítulo\n{CLAIM}"
    )
    unreachable = ContentSubmission(kind=ContentKind.LINK, url="https://ex.org/x", text=CLAIM)
    assert _normalizer(pages=pages).normalize(unreachable) == CLAIM
    short = ContentSubmission(kind=ContentKind.LINK, url="https://ex.org/x", text="é verdade?")
    with pytest.raises(ContentExtractionError):
        _normalizer(pages=pages).normalize(short)


# --------------------------------------------------------------------------- conteúdo principal


@dataclass
class OnePageFetcher:
    resource: FetchedResource

    def fetch(self, url: str) -> FetchedResource:
        return self.resource


def test_main_content_drops_navigation_related_links_and_comments() -> None:
    html = (
        "<html><head><title>Portal</title></head><body><nav>Início | Saúde</nav>"
        "<div class='cookie'>Usamos cookies. Aceitar</div><main><article><h1>Mensagem circula</h1>"
        "<p>A prefeitura divulgou a programação cultural do fim de semana na praça central.</p>"
        f"<p>{CLAIM}</p><div class='related'><h3>Leia também</h3><ul><li>A vacina da gripe causa "
        "gripe.</li></ul></div><section class='comments'><h3>Comentários</h3><p>Compartilhei."
        "</p></section></article></main><footer>Direitos reservados</footer></body></html>"
    )
    text = main_html_text(html)
    assert CLAIM in text
    assert "Leia também" not in text and "Início" not in text and "Compartilhei" not in text


def test_main_content_falls_back_to_tag_extraction_for_tiny_pages() -> None:
    html = f"<html><body><main><p>{CLAIM}</p></main></body></html>"
    assert CLAIM in main_html_text(html)


def test_login_walled_social_links_are_refused_before_fetching() -> None:
    assert is_login_walled("https://www.instagram.com/p/abc")
    assert is_login_walled("https://m.youtube.com/watch?v=1")
    assert not is_login_walled("https://www.gov.br/saude")
    extractor = MainContentLinkExtractor(fetcher=OnePageFetcher(None))  # type: ignore[arg-type]
    with pytest.raises(ContentExtractionError, match="login"):
        extractor.extract("https://x.com/perfil/status/1")
    assert "captura de tela" in LOGIN_WALL_MESSAGE


def test_main_content_extractor_reads_html_through_the_fetcher() -> None:
    body = f"<html><body><article><p>{CLAIM}</p></article></body></html>".encode()
    resource = FetchedResource("https://ex.org/a", "text/html; charset=utf-8", body)
    extractor = MainContentLinkExtractor(fetcher=OnePageFetcher(resource))  # type: ignore[arg-type]
    assert CLAIM in extractor.extract("https://ex.org/a")


def test_cleaner_leaves_every_clean_evaluation_claim_unchanged() -> None:
    from pathlib import Path

    from immunocheck.evaluation.end_to_end import load_end_to_end_items
    from immunocheck.evaluation.paraphrase_set import load_paraphrases

    root = Path(__file__).parents[1]
    items = load_end_to_end_items(root / "evaluation/refinement_v4/items.jsonl", require_reviewed=True)
    claims = [item.claim for item in items]
    claims += [p.claim for p in load_paraphrases(root / "evaluation/refinement_v5/paraphrases.jsonl")]
    assert all(clean_forwarded_text(claim) == " ".join(claim.split()) for claim in claims)
