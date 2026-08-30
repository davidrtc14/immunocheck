from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from immunocheck.domain.models import Evidence, ExtractedClaim
from immunocheck.retrieval.bm25 import BM25Index


class CorpusLoadError(RuntimeError):
    """Indica ausência ou inconsistência no corpus piloto processado."""


class PilotCorpusBM25Retriever:
    def __init__(self, evidence: Sequence[Evidence], *, top_k: int = 6) -> None:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        self._index = BM25Index(evidence)
        self._top_k = top_k

    @classmethod
    def from_jsonl(cls, path: Path, *, top_k: int = 6) -> PilotCorpusBM25Retriever:
        return cls(load_evidence_jsonl(path), top_k=top_k)

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        return self._index.search(claim.text, top_k=self._top_k)


def load_evidence_jsonl(path: Path) -> tuple[Evidence, ...]:
    if not path.is_file():
        raise CorpusLoadError(
            "Corpus processado ausente. Execute os scripts de download e construção do corpus."
        )
    evidence: list[Evidence] = []
    try:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                evidence.append(_parse_chunk(json.loads(line), line_number))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise CorpusLoadError("O corpus processado está inválido.") from exc
    if not evidence:
        raise CorpusLoadError("O corpus processado não contém trechos.")
    return tuple(evidence)


def _parse_chunk(chunk: dict[str, object], line_number: int) -> Evidence:
    required_text = ("chunk_id", "text", "source", "document_title", "url")
    for field in required_text:
        value = chunk[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Campo {field} inválido na linha {line_number}.")
    publication_date = chunk.get("publication_date")
    page = chunk.get("page_start")
    if publication_date is not None and not isinstance(publication_date, str):
        raise ValueError(f"Data inválida na linha {line_number}.")
    if not isinstance(page, int) or isinstance(page, bool) or page <= 0:
        raise ValueError(f"Página inválida na linha {line_number}.")
    return Evidence(
        chunk_id=str(chunk["chunk_id"]),
        text=str(chunk["text"]),
        source_name=str(chunk["source"]),
        document_title=str(chunk["document_title"]),
        url=str(chunk["url"]),
        publication_date=publication_date,
        page=page,
    )
