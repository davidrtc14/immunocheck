"""Limpeza determinística da entrada antes do extrator de alegação (ADR-050).

Remove o que não é alegação: emoji, marcadores de encaminhamento, chamadas para repassar,
pontuação repetida, texto todo em caixa alta e, no texto de OCR, os elementos de interface de
aplicativos de mensagem e redes sociais (hora, bateria, contadores, "online"). Nenhuma regra
reescreve palavras da alegação; números, negações e siglas curtas são preservados.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

_KEPT_SYMBOLS = frozenset("°ºª")
_INVISIBLE = frozenset({"\u200b", "\u200c", "\u200d", "\u2060", "\ufe0e", "\ufe0f"})
# Linha que é só o marcador ("Encaminhada") e a frase longa no meio do texto.
_FORWARD_LINE = re.compile(
    r"\W*(?:encaminhada|forwarded)(?:\s+(?:com\s+frequ[eê]ncia|many\s+times))?\W*",
    re.IGNORECASE,
)
_FORWARD_PHRASE = re.compile(
    r"\bencaminhada\s+com\s+frequ[eê]ncia\b|\bforwarded\s+many\s+times\b", re.IGNORECASE
)
_CALL_TO_ACTION = re.compile(
    r"^\W*(?:repassem?|compartilhem?|encaminhem?|divulguem?|espalhem?|mandem?\s+para)\b"
    r"|\bpara\s+todos\s+os\s+(?:grupos|contatos)\b",
    re.IGNORECASE,
)
_LEADING_ALERT = re.compile(
    r"^\W*(?:aten[cç][aã]o|urgente|alerta|importante|cuidado)\s*[!:.]+\s*", re.IGNORECASE
)
_REPEATED_MARKS = re.compile(r"([!?])[!?]+")
_URL = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)

_CLOCK = r"\d{1,2}[:h]\d{2}(?:\s*(?:am|pm))?"
_INTERFACE_LINE = re.compile(
    "|".join(
        (
            rf"^\W*{_CLOCK}(?:\s+\d{{1,3}}\s*%)?\W*$",  # hora; hora + bateria
            r"^\W*\d{1,3}\s*%\W*$",  # bateria
            r"^\W*(?:online|digitando\.*|gravando [aá]udio\.*|visto por [úu]ltimo.*)\W*$",
            r"^\W*(?:mensagem|digite uma mensagem|message)\W*$",
            r"^\W*(?:patrocinado|publicidade|sponsored)\W*$",
            (
                r"^\W*(?:responder|curtir|compartilhar|seguir)"
                r"(?:\W+(?:responder|curtir|compartilhar|seguir))*\W*$"
            ),
            (
                r"^.*\d+(?:[.,]\d+)?\s*(?:mil\s+)?(?:coment[aá]rios|curtidas|compartilhamentos"
                r"|visualiza[cç][oõ]es|reposts?|likes|views)\b.*$"
            ),
            r"^\W*@?\w+\s*[·.\-]\s*\d+\s*(?:h|min|d|s)\W*$",  # @perfil · 3 h
        )
    ),
    re.IGNORECASE,
)
# Palavras de interface que o OCR costuma deformar ("Mensaderm", "onhne").
_INTERFACE_WORDS = ("mensagem", "online", "digitando", "patrocinado")
_FORWARD_TEXT = "encaminhada com frequência"
_FUNCTION_WORDS = frozenset(
    {
        "a", "o", "e", "é", "as", "os", "ao", "à", "de", "do", "da", "dos", "das", "em", "no",
        "na", "nos", "nas", "um", "uma", "por", "que", "se", "com", "sem", "mas", "ou", "foi",
        "são", "tem", "já", "até", "seu", "sua", "nem", "não", "há", "só", "mais",
    }
)
_TRAILING_CLOCK = re.compile(rf"\s+{_CLOCK}\W*$", re.IGNORECASE)
_SENTENCE_END = re.compile(r"[.!?:;…]\s*$")


def strip_symbols(text: str) -> str:
    """NFKC, sem emoji nem caracteres invisíveis; mantém °, º e ª."""

    # NFKC desfaz ligaduras e larguras do OCR, mas transformaria "2ª" em "2a".
    normalized = "".join(
        char if char in _KEPT_SYMBOLS else unicodedata.normalize("NFKC", char) for char in text
    )
    return "".join(
        char
        for char in normalized
        if char in _KEPT_SYMBOLS
        or (char not in _INVISIBLE and unicodedata.category(char) not in {"So", "Sk", "Cs", "Co"})
    )


def clean_forwarded_text(text: str) -> str:
    """Limpa uma mensagem digitada ou encaminhada, preservando as quebras de parágrafo."""

    lines: list[str] = []
    for raw_line in strip_symbols(text).splitlines():
        if _FORWARD_LINE.fullmatch(raw_line):
            continue
        line = _FORWARD_PHRASE.sub(" ", raw_line)
        line = _REPEATED_MARKS.sub(r"\1", line)
        line = _LEADING_ALERT.sub("", line)
        line = " ".join(line.split())
        if not line or not re.search(r"\w", line):
            continue
        if _CALL_TO_ACTION.search(line) and len(line) < 80:
            continue
        lines.append(_soften_shouting(line))
    return "\n".join(lines)


def strip_interface_lines(text: str) -> str:
    """Remove linhas de interface do OCR e junta as linhas quebradas de um mesmo parágrafo."""

    kept: list[str] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if not line or _INTERFACE_LINE.match(line) or _FORWARD_LINE.fullmatch(line):
            continue
        line = _strip_garbled_forward(_TRAILING_CLOCK.sub("", line))
        if line and not _is_garbled_interface_word(line):
            kept.append(line)
    return join_wrapped_lines(kept)


def join_wrapped_lines(lines: list[str]) -> str:
    paragraphs: list[str] = []
    for line in lines:
        # Linha quebrada continua em minúscula ou dígito; maiúscula após linha sem pontuação
        # costuma ser outro elemento (nome do grupo, título), então fica em linha própria.
        continues = line[:1].islower() or line[:1].isdigit()
        if paragraphs and continues and not _SENTENCE_END.search(paragraphs[-1]):
            previous = paragraphs[-1]
            if previous.endswith("-") and line[:1].islower():
                paragraphs[-1] = previous[:-1] + line
            else:
                paragraphs[-1] = f"{previous} {line}"
        else:
            paragraphs.append(line)
    return "\n".join(paragraphs)


def split_message_link(text: str) -> tuple[str | None, str]:
    """Separa a primeira URL da mensagem do comentário ao redor."""

    match = _URL.search(text)
    if match is None:
        return None, text.strip()
    url = match.group(0).rstrip(".,;:!?)]}")
    commentary = text[: match.start()] + " " + text[match.start() + len(url) :]
    return url, " ".join(token for token in commentary.split() if re.search(r"\w", token))


def _soften_shouting(line: str) -> str:
    letters = [char for char in line if char.isalpha()]
    if len(letters) < 20 or sum(char.isupper() for char in letters) / len(letters) < 0.8:
        return line
    words = []
    for word in line.split():
        core = re.sub(r"\W", "", word)
        # Siglas curtas (HPV, BCG, SUS) e palavras com dígitos ficam como estão.
        is_acronym = len(core) <= 3 and core.lower() not in _FUNCTION_WORDS
        if is_acronym or any(char.isdigit() for char in core):
            words.append(word)
        else:
            words.append(word.lower())
    softened = " ".join(words)
    return softened[:1].upper() + softened[1:]


def _is_garbled_interface_word(line: str) -> bool:
    token = line.strip(" .:-").lower()
    return " " not in token and len(token) <= 12 and any(
        SequenceMatcher(None, token, word).ratio() >= 0.7 for word in _INTERFACE_WORDS
    )


def _strip_garbled_forward(line: str) -> str:
    """Remove um "Encaminhada com frequência" deformado pelo OCR no começo da linha."""

    words = line.split()
    for size in (3, 2):
        prefix = " ".join(words[:size]).lower()
        if len(words) >= size and SequenceMatcher(None, prefix, _FORWARD_TEXT).ratio() >= 0.6:
            return " ".join(words[size:])
    return line
