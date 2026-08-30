import json
from pathlib import Path

import pytest

from immunocheck.domain.models import ExtractedClaim
from immunocheck.retrieval.pilot_corpus import (
    CorpusLoadError,
    PilotCorpusBM25Retriever,
    load_evidence_jsonl,
)


def _chunk(chunk_id: str, text: str, page: int = 1) -> dict[str, object]:
    return {
        "chunk_id": chunk_id,
        "document_id": "doc",
        "text": text,
        "source": "Ministério da Saúde",
        "document_title": "Manual",
        "url": "https://www.gov.br/saude/manual.pdf",
        "page_start": page,
        "page_end": page,
        "publication_date": "2026-01-01",
    }


def test_loads_chunks_and_retrieves_relevant_evidence(tmp_path: Path) -> None:
    path = tmp_path / "chunks.jsonl"
    rows = [_chunk("hpv", "Vacinação contra HPV em adolescentes."), _chunk("flu", "Influenza.")]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    retriever = PilotCorpusBM25Retriever.from_jsonl(path, top_k=1)
    result = retriever.retrieve(ExtractedClaim("Vacina HPV para adolescentes", 0.9))

    assert result[0].chunk_id == "hpv"
    assert result[0].source_name == "Ministério da Saúde"


def test_rejects_missing_or_invalid_corpus(tmp_path: Path) -> None:
    with pytest.raises(CorpusLoadError, match="ausente"):
        load_evidence_jsonl(tmp_path / "missing.jsonl")

    invalid = tmp_path / "invalid.jsonl"
    invalid.write_text('{"chunk_id": "only-id"}\n', encoding="utf-8")
    with pytest.raises(CorpusLoadError, match="inválido"):
        load_evidence_jsonl(invalid)
