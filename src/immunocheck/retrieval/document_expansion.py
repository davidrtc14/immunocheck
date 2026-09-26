from __future__ import annotations

import re
from collections.abc import Sequence

from immunocheck.domain.models import Evidence

CHUNK_ID_PATTERN = re.compile(r"^(?P<document>.+):p(?P<page>\d+):c(?P<chunk>\d+):[^:]+$")


def expand_document_candidates(
    evidence: Sequence[Evidence],
    seed_ids: Sequence[str],
    *,
    first_chunks: int = 4,
    neighbor_radius: int = 1,
    max_candidates: int = 20,
) -> tuple[Evidence, ...]:
    """Expande sementes com passagens representativas e vizinhas do mesmo documento."""
    if first_chunks < 0 or neighbor_radius < 0 or max_candidates <= 0:
        raise ValueError("Os limites de expansão precisam ser não negativos e o máximo positivo.")
    by_id = {item.chunk_id: item for item in evidence}
    if any(seed_id not in by_id for seed_id in seed_ids):
        raise ValueError("A expansão recebeu uma semente ausente do corpus.")

    by_document: dict[str, list[Evidence]] = {}
    parsed: dict[str, tuple[str, int, int]] = {}
    for item in evidence:
        identity = _parse_chunk_id(item.chunk_id)
        parsed[item.chunk_id] = identity
        by_document.setdefault(identity[0], []).append(item)

    selected: list[Evidence] = []
    selected_ids: set[str] = set()

    def add(item: Evidence) -> None:
        if item.chunk_id not in selected_ids and len(selected) < max_candidates:
            selected.append(item)
            selected_ids.add(item.chunk_id)

    seeds = [by_id[seed_id] for seed_id in dict.fromkeys(seed_ids)]
    for item in seeds:
        add(item)
    for item in seeds:
        document_id, _, _ = parsed[item.chunk_id]
        for representative in by_document[document_id][:first_chunks]:
            add(representative)
    for item in seeds:
        document_id, page, chunk = parsed[item.chunk_id]
        for neighbor in by_document[document_id]:
            _, neighbor_page, neighbor_chunk = parsed[neighbor.chunk_id]
            if neighbor_page == page and abs(neighbor_chunk - chunk) <= neighbor_radius:
                add(neighbor)
    return tuple(selected)


def _parse_chunk_id(chunk_id: str) -> tuple[str, int, int]:
    match = CHUNK_ID_PATTERN.fullmatch(chunk_id)
    if match is None:
        raise ValueError("O corpus contém chunk_id incompatível com a expansão documental.")
    return match.group("document"), int(match.group("page")), int(match.group("chunk"))
