"""Benchmark sintético de extração multimodal com gabarito automático (ADR-050).

Cada caso parte de uma alegação v4 já rotulada e a embute em uma imagem, página ou mensagem
gerada aqui. O gabarito de extração é o próprio texto da alegação; nenhuma entrada real é usada.
A renderização é determinística por `case_id` (fontes do Windows, cujo hash é registrado).
"""

from __future__ import annotations

import hashlib
import io
import os
import random
import re
import textwrap
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from immunocheck.evaluation.end_to_end import EndToEndItem

FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
BENCHMARK_HOST = "https://extracao.invalid"

# Modelos de desenvolvimento servem à iteração; os reservados só aparecem na execução final.
IMAGE_TEMPLATES = {
    "clean": "control",
    "whatsapp_light": "development",
    "social_light": "development",
    "photo_whatsapp_light": "development",
    "low_res_forward": "development",
    "story_overlay": "development",
    "whatsapp_dark": "reserved",
    "meme": "reserved",
    "photo_social_dark": "reserved",
}
LINK_TEMPLATES = {
    "news_article": "development",
    "long_page": "development",
    "blog_divs": "reserved",
    "pdf_report": "reserved",
}
MESSAGE_TEMPLATES = {"comment_with_link": "development", "link_then_question": "reserved"}
TEXT_TEMPLATES = {
    "forward_emoji": "development",
    "caps_shout": "development",
    "inline_url": "reserved",
    "two_claims": "reserved",
}
MODALITY_TEMPLATES = {
    "image": IMAGE_TEMPLATES,
    "link": LINK_TEMPLATES,
    "message": MESSAGE_TEMPLATES,
    "text": TEXT_TEMPLATES,
}
FONTS_USED = (
    "arial.ttf",
    "segoeui.ttf",
    "segoeuib.ttf",
    "segoeuii.ttf",
    "tahoma.ttf",
    "tahomabd.ttf",
    "impact.ttf",
    "trebuc.ttf",
    "trebucbd.ttf",
)

_NEUTRAL_SENTENCES = (
    "A prefeitura divulgou a programação cultural do fim de semana na praça central.",
    "O trânsito na avenida principal foi alterado por causa das obras de drenagem.",
    "A feira de artesanato reúne expositores de vários bairros até domingo.",
    "Moradores relataram que a coleta seletiva passou a ocorrer às quartas-feiras.",
    "A biblioteca municipal ampliou o horário de funcionamento durante as férias.",
    "O campeonato de futsal do bairro terá a final disputada no ginásio novo.",
    "A previsão indica tempo firme, com temperaturas amenas no início da manhã.",
    "Uma oficina gratuita de fotografia está com inscrições abertas na escola técnica.",
    "O mercado público passa por reforma e deve reabrir no próximo trimestre.",
    "A linha de ônibus que atende o centro ganhou dois horários extras à noite.",
    "Voluntários organizaram um mutirão de limpeza no parque da cidade.",
    "O festival gastronômico terá barracas de comidas típicas e música ao vivo.",
)
_COMMENTS = (
    "Compartilhei com a família.",
    "Alguém tem a fonte disso?",
    "Recebi no grupo do trabalho também.",
    "Vou mandar para minha mãe ler.",
)
_GROUP_NAMES = ("Grupo da Família", "Tia Rosa", "Amigos do Bairro", "Turma da Escola")
_LEAD_MESSAGES = ("Olha isso gente", "Vocês viram isso?", "Recebi agora", "Leiam antes que apaguem")
_PAGE_NAMES = ("Saúde Sem Censura", "Notícias do Povo", "Verdade Revelada", "Portal Alerta")


@dataclass(frozen=True, slots=True)
class ExtractionCase:
    case_id: str
    parent_item_id: str
    item_split: str
    modality: str
    template: str
    template_split: str
    target_claim: str
    expected_label: str
    claim_family: str
    distractors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RenderedImage:
    data: bytes
    media_type: str
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class RenderedPage:
    url: str
    content_type: str
    body: bytes


def build_cases(items: Sequence[EndToEndItem]) -> list[ExtractionCase]:
    """Um caso por item e modelo; distratores vêm de outras famílias do mesmo split."""

    cases: list[ExtractionCase] = []
    for item in items:
        pool = [
            other.claim
            for other in items
            if other.split is item.split and other.claim_family != item.claim_family
        ]
        rng = _rng(item.item_id, "distractors")
        distractors = tuple(rng.sample(pool, k=min(3, len(pool))))
        for modality, templates in MODALITY_TEMPLATES.items():
            for template, template_split in templates.items():
                cases.append(
                    ExtractionCase(
                        case_id=f"{item.item_id}-{modality}-{template}",
                        parent_item_id=item.item_id,
                        item_split=item.split.value,
                        modality=modality,
                        template=template,
                        template_split=template_split,
                        target_claim=item.claim,
                        expected_label=item.label.value,
                        claim_family=item.claim_family,
                        distractors=distractors,
                    )
                )
    return cases


def font_hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((FONT_DIR / name).read_bytes()).hexdigest() for name in FONTS_USED
    }


# --------------------------------------------------------------------------- imagens


def render_image(case: ExtractionCase) -> RenderedImage:
    rng = _rng(case.case_id, "image")
    claim = case.target_claim
    if case.template == "clean":
        return _encode(_clean(claim), "PNG")
    if case.template == "whatsapp_light":
        return _encode(_whatsapp(claim, rng, dark=False), "JPEG", quality=85)
    if case.template == "whatsapp_dark":
        return _encode(_whatsapp(claim, rng, dark=True), "JPEG", quality=85)
    if case.template == "social_light":
        return _encode(_social(claim, rng, dark=False), "JPEG", quality=85)
    if case.template == "meme":
        return _encode(_meme(claim, rng), "JPEG", quality=80)
    if case.template == "low_res_forward":
        return _encode(_downscaled(_whatsapp(claim, rng, dark=False), 0.45), "JPEG", quality=30)
    if case.template == "story_overlay":
        return _encode(_story(claim, rng), "JPEG", quality=80)
    if case.template == "photo_whatsapp_light":
        base = _whatsapp(claim, rng, dark=False)
        return _encode(_screen_photo(base, rng, strength=1.0), "JPEG", quality=45)
    if case.template == "photo_social_dark":
        base = _social(claim, rng, dark=True)
        return _encode(_screen_photo(base, rng, strength=1.4), "JPEG", quality=35)
    raise ValueError(f"Modelo de imagem desconhecido: {case.template}")


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if font.getlength(candidate) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _clean(claim: str) -> Image.Image:
    font = _font("arial.ttf", 44)
    lines = _wrap(claim, font, 1280)
    image = Image.new("RGB", (1400, 120 + 58 * len(lines)), "white")
    draw = ImageDraw.Draw(image)
    for index, line in enumerate(lines):
        draw.text((60, 60 + 58 * index), line, fill="black", font=font)
    return image


def _whatsapp(claim: str, rng: random.Random, *, dark: bool) -> Image.Image:
    palette = (
        {"header": "#202C33", "head_text": "#E9EDEF", "wall": "#0B141A", "bubble": "#005C4B",
         "lead": "#202C33", "text": "#E9EDEF", "meta": "#8696A0", "bar": "#1F2C34"}
        if dark
        else {"header": "#008069", "head_text": "#FFFFFF", "wall": "#EFEAE2", "bubble": "#FFFFFF",
              "lead": "#FFFFFF", "text": "#111B21", "meta": "#667781", "bar": "#F0F2F5"}
    )
    regular, bold, italic = (
        ("tahoma.ttf", "tahomabd.ttf", "tahoma.ttf")
        if dark
        else ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf")
    )
    width = 1080
    body = _font(regular, 38)
    lines = _wrap(claim, body, width - 220)
    bubble_height = 70 + 52 * len(lines) + 50
    height = 80 + 130 + 40 + 90 + 30 + bubble_height + 60 + 120
    image = Image.new("RGB", (width, height), palette["wall"])
    draw = ImageDraw.Draw(image)
    hour, minute = rng.randint(7, 22), rng.randint(10, 59)
    draw.rectangle((0, 0, width, 210), fill=palette["header"])
    draw.text((40, 22), f"{hour}:{minute + 1:02d}", fill=palette["head_text"], font=_font(bold, 30))
    draw.text((width - 120, 22), f"{rng.randint(20, 99)}%", fill=palette["head_text"],
              font=_font(regular, 30))
    draw.ellipse((40, 100, 120, 180), fill=palette["meta"])
    draw.text((145, 100), rng.choice(_GROUP_NAMES), fill=palette["head_text"], font=_font(bold, 38))
    draw.text((145, 148), "online", fill=palette["head_text"], font=_font(regular, 28))
    top = 250
    lead = rng.choice(_LEAD_MESSAGES)
    lead_font = _font(regular, 36)
    lead_width = int(lead_font.getlength(lead)) + 170
    draw.rounded_rectangle((40, top, 40 + lead_width, top + 90), 18, fill=palette["lead"])
    draw.text((70, top + 20), lead, fill=palette["text"], font=lead_font)
    draw.text((40 + lead_width - 95, top + 52), f"{hour}:{minute - 1:02d}", fill=palette["meta"],
              font=_font(regular, 24))
    top += 120
    draw.rounded_rectangle((40, top, width - 60, top + bubble_height), 18, fill=palette["bubble"])
    draw.text((75, top + 18), "Encaminhada com frequência", fill=palette["meta"],
              font=_font(italic, 28))
    for index, line in enumerate(lines):
        draw.text((75, top + 70 + 52 * index), line, fill=palette["text"], font=body)
    draw.text((width - 160, top + bubble_height - 42), f"{hour}:{minute:02d}",
              fill=palette["meta"], font=_font(regular, 24))
    draw.rectangle((0, height - 120, width, height), fill=palette["bar"])
    draw.rounded_rectangle((30, height - 100, width - 130, height - 20), 40,
                           fill=palette["lead"])
    draw.text((80, height - 80), "Mensagem", fill=palette["meta"], font=_font(regular, 32))
    return image


def _social(claim: str, rng: random.Random, *, dark: bool) -> Image.Image:
    background, text, meta, line = (
        ("#15202B", "#F7F9F9", "#8B98A5", "#38444D")
        if dark
        else ("#FFFFFF", "#0F1419", "#536471", "#EFF3F4")
    )
    regular, bold = ("trebuc.ttf", "trebucbd.ttf") if dark else ("segoeui.ttf", "segoeuib.ttf")
    width = 1080
    body = _font(regular, 40)
    lines = _wrap(claim, body, width - 120)
    height = 200 + 56 * len(lines) + 170
    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    name = rng.choice(_PAGE_NAMES)
    handle = "@" + re.sub(r"\W", "", _strip_accents(name)).lower()
    draw.ellipse((60, 50, 160, 150), fill=rng.choice(("#1D9BF0", "#F91880", "#7856FF", "#FF7A00")))
    draw.text((185, 58), name, fill=text, font=_font(bold, 36))
    draw.text((185, 104), f"{handle} · {rng.randint(1, 23)} h", fill=meta, font=_font(regular, 30))
    for index, row in enumerate(lines):
        draw.text((60, 190 + 56 * index), row, fill=text, font=body)
    footer = 190 + 56 * len(lines) + 40
    draw.line((60, footer, width - 60, footer), fill=line, width=2)
    counts = (
        f"{rng.randint(1, 9)},{rng.randint(1, 9)} mil comentários   "
        f"{rng.randint(1, 9)},{rng.randint(1, 9)} mil compartilhamentos   "
        f"{rng.randint(10, 99)} mil curtidas"
    )
    draw.text((60, footer + 30), counts, fill=meta, font=_font(regular, 28))
    return image


def _photo_background(rng: random.Random, width: int, height: int) -> Image.Image:
    """Fundo desfocado com cores aleatórias, imitando uma foto atrás do texto."""

    top_color = np.array([rng.randint(20, 120) for _ in range(3)], dtype=np.float32)
    bottom_color = np.array([rng.randint(120, 230) for _ in range(3)], dtype=np.float32)
    ramp = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None, None]
    canvas = np.repeat(top_color * (1 - ramp) + bottom_color * ramp, width, axis=1)
    noise_rng = np.random.default_rng(rng.randint(0, 2**31))
    canvas += noise_rng.normal(0, 14, canvas.shape)
    image = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(image)
    for _ in range(9):
        x, y, radius = rng.randint(0, width), rng.randint(0, height), rng.randint(60, 220)
        shade = tuple(rng.randint(40, 230) for _ in range(3))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=shade)
    return image.filter(ImageFilter.GaussianBlur(9))


def _meme(claim: str, rng: random.Random) -> Image.Image:
    width = 1080
    font = _font("impact.ttf", 64)
    lines = _wrap(claim.upper(), font, width - 120)
    image = _photo_background(rng, width, max(1080, 160 + 78 * len(lines)))
    draw = ImageDraw.Draw(image)
    for index, line in enumerate(lines):
        line_width = font.getlength(line)
        draw.text(((width - line_width) / 2, 80 + 78 * index), line, fill="white", font=font,
                  stroke_width=4, stroke_fill="black")
    return image


def _story(claim: str, rng: random.Random) -> Image.Image:
    width, height = 1080, 1350
    font = _font("segoeuib.ttf", 46)
    lines = _wrap(claim, font, width - 240)
    image = _photo_background(rng, width, height).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    box_height = 80 + 62 * len(lines)
    top = (height - box_height) // 2
    draw.rounded_rectangle((80, top, width - 80, top + box_height), 30, fill=(0, 0, 0, 120))
    image = Image.alpha_composite(image, overlay).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.text((60, 50), rng.choice(_PAGE_NAMES), fill="white", font=_font("segoeuib.ttf", 32))
    draw.text((60, 95), "Patrocinado", fill="#DDDDDD", font=_font("segoeui.ttf", 26))
    for index, line in enumerate(lines):
        line_width = font.getlength(line)
        draw.text(((width - line_width) / 2, top + 40 + 62 * index), line, fill="white", font=font)
    return image


def _downscaled(image: Image.Image, factor: float) -> Image.Image:
    size = (int(image.width * factor), int(image.height * factor))
    return image.resize(size, Image.Resampling.LANCZOS)


def _screen_photo(base: Image.Image, rng: random.Random, *, strength: float) -> Image.Image:
    array = cv2.cvtColor(np.asarray(base), cv2.COLOR_RGB2BGR)
    height, width = array.shape[:2]
    border = int(0.08 * max(width, height))
    array = cv2.copyMakeBorder(array, border, border, border, border, cv2.BORDER_CONSTANT,
                               value=(32, 32, 36))
    full_h, full_w = array.shape[:2]
    jitter = 0.035 * strength
    source = np.float32([[0, 0], [full_w, 0], [full_w, full_h], [0, full_h]])
    target = np.float32(
        [
            [x + rng.uniform(-jitter, jitter) * full_w, y + rng.uniform(-jitter, jitter) * full_h]
            for x, y in source
        ]
    )
    matrix = cv2.getPerspectiveTransform(source, target)
    array = cv2.warpPerspective(array, matrix, (full_w, full_h), borderValue=(32, 32, 36))
    angle = rng.uniform(2.0, 4.0) * strength * rng.choice((-1, 1))
    rotation = cv2.getRotationMatrix2D((full_w / 2, full_h / 2), angle, 1.0)
    array = cv2.warpAffine(array, rotation, (full_w, full_h), borderValue=(32, 32, 36))
    array = cv2.GaussianBlur(array, (0, 0), 0.9 * strength)
    y_grid, x_grid = np.mgrid[0:full_h, 0:full_w].astype(np.float32)
    distance = np.hypot((x_grid - full_w / 2) / full_w, (y_grid - full_h / 2) / full_h)
    vignette = 1.0 - 0.45 * strength * distance[..., None]
    noise_rng = np.random.default_rng(rng.randint(0, 2**31))
    noisy = array.astype(np.float32) * vignette + noise_rng.normal(0, 7 * strength, array.shape)
    array = np.clip(noisy, 0, 255).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(array, cv2.COLOR_BGR2RGB))


def _encode(image: Image.Image, image_format: str, *, quality: int = 90) -> RenderedImage:
    buffer = io.BytesIO()
    if image_format == "JPEG":
        image.save(buffer, "JPEG", quality=quality)
        media_type = "image/jpeg"
    else:
        image.save(buffer, "PNG")
        media_type = "image/png"
    return RenderedImage(buffer.getvalue(), media_type, image.width, image.height)


# --------------------------------------------------------------------------- links e mensagens


def page_url(case: ExtractionCase) -> str:
    suffix = "relatorio.pdf" if case.template == "pdf_report" else "materia"
    return f"{BENCHMARK_HOST}/{case.parent_item_id}/{case.template}/{suffix}"


def render_page(case: ExtractionCase) -> RenderedPage:
    """Página da modalidade `link` ou a página apontada por uma `message`."""

    rng = _rng(case.case_id, "page")
    claim = _escape(case.target_claim)
    first, second, third = (_escape(item) for item in (*case.distractors, "", "", "")[:3])
    url = page_url(case)
    template = "news_article" if case.modality == "message" else case.template
    if template == "pdf_report":
        return RenderedPage(url, "application/pdf", _pdf_report(case.target_claim, rng))
    if template == "news_article":
        body = (
            "<header><nav>Início | Saúde | Política | Esportes | Contato</nav></header>"
            "<div class='cookie-banner'>Usamos cookies para melhorar sua experiência. Ao continuar "
            "navegando, você concorda com a nossa política de privacidade. Aceitar</div>"
            "<main><article><h1>Mensagem sobre vacinas circula nas redes</h1>"
            f"<p class='byline'>Por Redação · atualizado às {rng.randint(8, 20)}h"
            f"{rng.randint(10, 59)}</p>"
            f"<p>{_neutral(rng, 2)}</p><p>{claim}</p><p>{_neutral(rng, 2)}</p>"
            f"<div class='related'><h3>Leia também</h3><ul><li>{first}</li><li>{second}</li>"
            "</ul></div>"
            f"<section class='comments'><h3>Comentários (2)</h3><p>{rng.choice(_COMMENTS)}</p>"
            f"<p>{rng.choice(_COMMENTS)}</p></section></article></main>"
            "<footer>© Portal de Notícias. Todos os direitos reservados.</footer>"
        )
    elif template == "long_page":
        filler = "".join(f"<p>{_neutral(rng, 4)}</p>" for _ in range(22))
        body = (
            "<header><nav>Início | Cidade | Cultura | Agenda</nav></header>"
            "<main><article><h1>Resumo da semana no município</h1>"
            f"{filler}<h2>Corrente compartilhada nos grupos</h2><p>{claim}</p>"
            f"<p>{_neutral(rng, 2)}</p></article></main>"
        )
    elif template == "blog_divs":
        body = (
            "<div id='app'><div class='topbar'>Blog Vida Natural · Assine · Entrar</div>"
            f"<div class='sidebar'><b>Mais lidos</b><div>{first}</div><div>{second}</div>"
            f"<div>{third}</div></div>"
            "<div class='post'><div class='post-title'>O que ninguém te conta</div>"
            f"<div class='post-body'><div>{_neutral(rng, 2)}</div><div><b>{claim}</b></div>"
            f"<div>{_neutral(rng, 3)}</div></div></div>"
            "<div class='newsletter-modal'>Assine nossa newsletter e receba conteúdos exclusivos "
            "toda semana. Digite seu e-mail.</div>"
            f"<div class='comments'>{rng.choice(_COMMENTS)} {rng.choice(_COMMENTS)}</div></div>"
        )
    else:
        raise ValueError(f"Modelo de página desconhecido: {template}")
    html = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        f"<title>{'Blog Vida Natural' if template == 'blog_divs' else 'Portal de Notícias'}"
        f"</title></head><body>{body}</body></html>"
    )
    return RenderedPage(url, "text/html; charset=utf-8", html.encode("utf-8"))


def render_message(case: ExtractionCase) -> str:
    rng = _rng(case.case_id, "message")
    url = page_url(case)
    if case.template == "comment_with_link":
        comment = rng.choice(("Recebi esse link no grupo, é verdade?", "Isso procede?"))
        return f"{comment} {url}"
    if case.template == "link_then_question":
        return f"{url}\nAlguém sabe se essa matéria está certa?"
    raise ValueError(f"Modelo de mensagem desconhecido: {case.template}")


def render_text(case: ExtractionCase) -> str:
    rng = _rng(case.case_id, "text")
    claim = case.target_claim
    if case.template == "forward_emoji":
        return (
            f"⚠️🚨 Encaminhada com frequência 🚨⚠️\n{claim} 😱😱\n"
            f"REPASSEM PARA TODOS OS GRUPOS!!! 🙏{'🙏' * rng.randint(0, 3)}"
        )
    if case.template == "caps_shout":
        return f"ATENÇÃO!!! {claim.upper()}!!! NINGUÉM FALA SOBRE ISSO!!!"
    if case.template == "inline_url":
        return f"{claim} Veja mais em {BENCHMARK_HOST}/v/{rng.randint(1000, 9999)} e compartilhe."
    if case.template == "two_claims":
        other = case.distractors[0] if case.distractors else ""
        return f"{claim} E tem mais: {other}"
    raise ValueError(f"Modelo de texto desconhecido: {case.template}")


def _pdf_report(claim: str, rng: random.Random) -> bytes:
    pages = (
        ["Boletim informativo da comunidade", _neutral(rng, 3)],
        ["Mensagens recebidas pela equipe", _neutral(rng, 1), claim, _neutral(rng, 1)],
        ["Expediente", _neutral(rng, 2)],
    )
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
            NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
        }
    )
    for paragraphs in pages:
        page = writer.add_blank_page(width=595, height=842)
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
        commands = ["BT /F1 11 Tf 14 TL 50 780 Td"]
        for paragraph in paragraphs:
            for line in textwrap.wrap(paragraph, 90) + [""]:
                escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
                commands.append(f"({escaped}) Tj T*")
        commands.append("ET")
        content = DecodedStreamObject()
        content.set_data("\n".join(commands).encode("cp1252", errors="replace"))
        page[NameObject("/Contents")] = writer._add_object(content)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _neutral(rng: random.Random, count: int) -> str:
    return " ".join(rng.sample(_NEUTRAL_SENTENCES, k=count))


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------- métricas


def normalize_for_cer(text: str, *, strip_accents: bool = False) -> str:
    normalized = unicodedata.normalize("NFC", text).casefold()
    if strip_accents:
        normalized = _strip_accents(normalized)
    return " ".join(normalized.split())


def substring_cer(reference: str, hypothesis: str, *, strip_accents: bool = False) -> float:
    """Distância de edição da alegação ao melhor trecho da extração, dividida pelo tamanho dela.

    Início e fim livres na hipótese: texto de interface ao redor (nome, hora, banner) não pesa;
    o que pesa é a alegação ter sido lida corretamente. 0 = idêntica; 1 = ausente.
    """

    ref = normalize_for_cer(reference, strip_accents=strip_accents)
    hyp = normalize_for_cer(hypothesis, strip_accents=strip_accents)
    if not ref:
        raise ValueError("A referência do CER não pode ser vazia.")
    previous = [0] * (len(hyp) + 1)
    for index, ref_char in enumerate(ref, start=1):
        current = [index] + [0] * len(hyp)
        for column, hyp_char in enumerate(hyp, start=1):
            current[column] = min(
                previous[column] + 1,
                current[column - 1] + 1,
                previous[column - 1] + (ref_char != hyp_char),
            )
        previous = current
    return min(1.0, min(previous) / len(ref))


_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_NEGATIONS = frozenset({"nao", "nunca", "jamais", "nenhum", "nenhuma", "nem", "sem"})


def markers_preserved(reference: str, hypothesis: str) -> bool:
    """Números e negações da alegação continuam presentes no texto extraído."""

    ref = normalize_for_cer(reference, strip_accents=True)
    hyp = normalize_for_cer(hypothesis, strip_accents=True)
    numbers_ok = set(_NUMBER.findall(ref)) <= set(_NUMBER.findall(hyp))
    ref_tokens, hyp_tokens = set(re.findall(r"\w+", ref)), set(re.findall(r"\w+", hyp))
    return numbers_ok and (ref_tokens & _NEGATIONS) <= hyp_tokens


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _seed(*parts: str) -> int:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _rng(*parts: str) -> random.Random:
    return random.Random(_seed(*parts))
