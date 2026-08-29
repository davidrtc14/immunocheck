from __future__ import annotations

import re
import unicodedata

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize_portuguese(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return TOKEN_PATTERN.findall(without_accents)
