"""Conjunto contrastivo C7 gerado do corpus, com rótulo por construção (ADR-052).

Cada chunk do corpus rende uma versão fiel (`SUPPORTED`), uma contradita (`REFUTED`) e uma
distorcida (`MISLEADING`) do mesmo fato; documentos baixados mas fora do corpus e relatos de caso
particular rendem `INSUFFICIENT_EVIDENCE`. Os portões automáticos descartam candidatos que copiam o
texto, que citam trecho inexistente ou que trazem número sem forma equivalente na fonte. As regras
estão em `evaluation/refinement_v7/PROTOCOL.md`; a geração por LLM e os embeddings ficam no script
`scripts/build_contrastive_set.py`, e este módulo só tem funções puras.
"""

from __future__ import annotations

import random
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from immunocheck.application.grounding import alnum_key
from immunocheck.application.tolerant_verification import unsupported_numbers

SUPPORTED, REFUTED, MISLEADING, INSUFFICIENT = (
    "SUPPORTED",
    "REFUTED",
    "MISLEADING",
    "INSUFFICIENT_EVIDENCE",
)
LABELS = (SUPPORTED, REFUTED, MISLEADING, INSUFFICIENT)
CORPUS_LABELS = (SUPPORTED, REFUTED, MISLEADING)
MISLEADING_SUBTYPES = (
    "overgeneralization",
    "causal_leap",
    "dropped_qualifier",
    "false_implication",
)
ORIGIN_CORPUS = "corpus_chunk"
ORIGIN_OUTSIDE = "outside_corpus_fact"
ORIGIN_INDIVIDUAL = "individual_event"

COPY_NGRAM = 4
MAX_COPY_OVERLAP = 0.30
MIN_QUOTE_CHARS = 20
DUPLICATE_SIMILARITY = 0.92
OUT_OF_CORPUS_SIMILARITY = 0.85
MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 2_500
COVERAGE_TOP_K = 5
COVERAGE_RELATIONS = ("supports", "contradicts", "partial", "none")
REVIEW_VERDICTS = ("correct", "incorrect", "ambiguous")
_REVIEW_ALIASES = {"correto": "correct", "incorreto": "incorrect", "ambiguo": "ambiguous"}

_VACCINE = re.compile(r"vacin|vaccin|imuniz|immuni", re.IGNORECASE)
_REFERENCE_LINE = re.compile(r"^\s*(?:\[?\d+[\].]|doi:|https?://|et al\.)", re.IGNORECASE)
_WORD = re.compile(r"\w+")


@dataclass(frozen=True, slots=True)
class SourceChunk:
    chunk_id: str
    document_id: str
    text: str
    theme: str
    origin: str = ORIGIN_CORPUS


@dataclass(frozen=True, slots=True)
class Candidate:
    label: str
    claim: str
    source: SourceChunk
    origin_type: str
    evidence_quote: str | None = None
    subtype: str | None = None
    sustained_part: str | None = None
    distortion: str | None = None


@dataclass(slots=True)
class GateReport:
    accepted: list[Candidate] = field(default_factory=list)
    rejected: Counter[str] = field(default_factory=Counter)


def is_candidate_chunk(text: str) -> bool:
    """Chunk com tamanho útil, sobre vacinação e sem cara de lista de referências."""

    if not MIN_CHUNK_CHARS <= len(text) <= MAX_CHUNK_CHARS or not _VACCINE.search(text):
        return False
    lines = [line for line in text.splitlines() if line.strip()]
    references = sum(bool(_REFERENCE_LINE.match(line)) for line in lines)
    digits = sum(char.isdigit() for char in text)
    return references <= max(1, len(lines) // 4) and digits / len(text) <= 0.15


def sample_chunks(
    chunks: Sequence[SourceChunk], *, per_document: int, seed: int = 42
) -> list[SourceChunk]:
    """Até `per_document` chunks candidatos por documento, sorteados com semente fixa."""

    by_document: dict[str, list[SourceChunk]] = defaultdict(list)
    for chunk in chunks:
        if is_candidate_chunk(chunk.text):
            by_document[chunk.document_id].append(chunk)
    rng = random.Random(seed)
    sampled: list[SourceChunk] = []
    for document_id in sorted(by_document):
        group = sorted(by_document[document_id], key=lambda chunk: chunk.chunk_id)
        rng.shuffle(group)
        sampled.extend(group[:per_document])
    return sampled


def copy_overlap(claim: str, source: str, n: int = COPY_NGRAM) -> float:
    """Fração dos n-gramas de palavras da alegação que aparecem literalmente na fonte."""

    claim_ngrams = _ngrams(_tokens(claim), n)
    if not claim_ngrams:
        return 0.0
    return len(claim_ngrams & _ngrams(_tokens(source), n)) / len(claim_ngrams)


def quote_in_chunk(quote: str | None, chunk_text: str) -> bool:
    if not isinstance(quote, str):
        return False
    key = alnum_key(quote)
    return len(key) >= MIN_QUOTE_CHARS and key in alnum_key(chunk_text)


def numbers_supported(claim: str, chunk_text: str) -> bool:
    return unsupported_numbers(claim, chunk_text) == ()


def gate_corpus_payload(payload: Mapping[str, object], source: SourceChunk) -> GateReport:
    """Portões 1 a 4 do protocolo sobre a resposta do gerador para um chunk do corpus."""

    report = GateReport()
    if payload.get("usable") is not True:
        report.rejected["chunk_sem_fato"] += 1
        return report
    quote = payload.get("evidence_quote")
    if not quote_in_chunk(quote if isinstance(quote, str) else None, source.text):
        report.rejected["trecho_inexistente"] += 1
        return report
    versions = {label: _text(payload.get(key)) for label, key in _VERSION_KEYS.items()}
    if any(not value for value in versions.values()):
        report.rejected["versao_vazia"] += 1
        return report
    if len({alnum_key(value) for value in versions.values()}) < len(versions):
        report.rejected["versoes_iguais"] += 1
        return report
    subtype = _text(payload.get("misleading_subtype"))
    for label, claim in versions.items():
        if not _VACCINE.search(claim):
            report.rejected[f"sem_vacina_{label}"] += 1
            continue
        if copy_overlap(claim, source.text) > MAX_COPY_OVERLAP:
            report.rejected[f"copia_{label}"] += 1
            continue
        if label == SUPPORTED and not numbers_supported(claim, source.text):
            report.rejected["numero_sem_fonte"] += 1
            continue
        if label == MISLEADING and subtype not in MISLEADING_SUBTYPES:
            report.rejected["subtipo_invalido"] += 1
            continue
        report.accepted.append(
            Candidate(
                label=label,
                claim=claim,
                source=source,
                origin_type=ORIGIN_CORPUS,
                evidence_quote=" ".join(str(quote).split()),
                subtype=subtype if label == MISLEADING else None,
                sustained_part=_text(payload.get("sustained_part"))
                if label == MISLEADING
                else None,
                distortion=_text(payload.get("distortion")) if label == MISLEADING else None,
            )
        )
    return report


def gate_outside_payload(payload: Mapping[str, object], source: SourceChunk) -> GateReport:
    """Fato de documento fora do corpus: trecho real, sem cópia e com números da fonte."""

    report = GateReport()
    claim = _text(payload.get("claim"))
    quote = payload.get("evidence_quote")
    if payload.get("usable") is not True or not claim:
        report.rejected["chunk_sem_fato"] += 1
    elif not quote_in_chunk(quote if isinstance(quote, str) else None, source.text):
        report.rejected["trecho_inexistente"] += 1
    elif not _VACCINE.search(claim):
        report.rejected["sem_vacina"] += 1
    elif copy_overlap(claim, source.text) > MAX_COPY_OVERLAP:
        report.rejected["copia"] += 1
    elif not numbers_supported(claim, source.text):
        report.rejected["numero_sem_fonte"] += 1
    else:
        report.accepted.append(
            Candidate(
                label=INSUFFICIENT,
                claim=claim,
                source=source,
                origin_type=ORIGIN_OUTSIDE,
                evidence_quote=" ".join(str(quote).split()),
            )
        )
    return report


def gate_individual_payload(payload: Mapping[str, object], source: SourceChunk) -> GateReport:
    report = GateReport()
    claim = _text(payload.get("claim"))
    if not claim or len(claim) < 40:
        report.rejected["relato_vazio"] += 1
    elif not _VACCINE.search(claim):
        report.rejected["sem_vacina"] += 1
    elif copy_overlap(claim, source.text) > MAX_COPY_OVERLAP:
        report.rejected["copia"] += 1
    else:
        report.accepted.append(
            Candidate(label=INSUFFICIENT, claim=claim, source=source, origin_type=ORIGIN_INDIVIDUAL)
        )
    return report


def coverage_keeps(payload: Mapping[str, object]) -> bool:
    """Portão 8: o fato fora do corpus fica só se nenhum chunk próximo resolver a alegação."""

    return payload.get("relation") == "none"


def normalize_review_verdict(value: object) -> str | None:
    """Aceita o valor da página (`correct`) e a forma em português (`Correto`, `Ambíguo`)."""

    if not isinstance(value, str):
        return None
    key = "".join(_tokens(value))
    key = _REVIEW_ALIASES.get(key, key)
    return key if key in REVIEW_VERDICTS else None


def near_duplicates(
    vectors: NDArray[np.float32], threshold: float = DUPLICATE_SIMILARITY
) -> set[int]:
    """Índices a descartar: cada um repete (cosseno ≥ limiar) um anterior que ficou."""

    normalized = _normalize_rows(vectors)
    dropped: set[int] = set()
    kept: list[int] = []
    for index in range(len(normalized)):
        if kept and float(np.max(normalized[kept] @ normalized[index])) >= threshold:
            dropped.add(index)
        else:
            kept.append(index)
    return dropped


def max_similarity(
    vectors: NDArray[np.float32], corpus_vectors: NDArray[np.float32]
) -> NDArray[np.float32]:
    """Maior cosseno de cada alegação contra todos os chunks do corpus."""

    if len(vectors) == 0:
        return np.empty(0, dtype=np.float32)
    scores = _normalize_rows(vectors) @ _normalize_rows(corpus_vectors).T
    return np.asarray(scores.max(axis=1), dtype=np.float32)


def split_documents(themes: Mapping[str, str], seed: int = 42) -> dict[str, str]:
    """Metade dos documentos de cada tema em desenvolvimento e metade em teste."""

    rng = random.Random(seed)
    by_theme: dict[str, list[str]] = defaultdict(list)
    for document_id, theme in themes.items():
        by_theme[theme].append(document_id)
    assignment: dict[str, str] = {}
    offset = 0
    for theme in sorted(by_theme):
        group = sorted(by_theme[theme])
        rng.shuffle(group)
        for index, document_id in enumerate(group):
            # O deslocamento alterna quem começa em cada tema, para equilibrar temas ímpares.
            assignment[document_id] = "development" if (index + offset) % 2 == 0 else "test"
        offset += len(group)
    return assignment


def assemble(candidates: Iterable[Candidate], *, per_label: int, seed: int = 42) -> list[Candidate]:
    """Um item por chunk, escolhendo o rótulo menos preenchido entre os disponíveis no chunk."""

    by_chunk: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        by_chunk[candidate.source.chunk_id].append(candidate)
    order = sorted(by_chunk)
    random.Random(seed).shuffle(order)
    counts: Counter[str] = Counter()
    selected: list[Candidate] = []
    for chunk_id in order:
        options = {candidate.label: candidate for candidate in by_chunk[chunk_id]}
        open_labels = [label for label in LABELS if label in options and counts[label] < per_label]
        if not open_labels:
            continue
        label = min(open_labels, key=lambda item: (counts[item], LABELS.index(item)))
        counts[label] += 1
        selected.append(options[label])
    return selected


_VERSION_KEYS = {SUPPORTED: "supported", REFUTED: "refuted", MISLEADING: "misleading"}


def _text(value: object) -> str:
    return " ".join(value.split()) if isinstance(value, str) else ""


def _tokens(text: str) -> list[str]:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    folded = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _WORD.findall(folded)


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1)}


def _normalize_rows(vectors: NDArray[np.float32]) -> NDArray[np.float32]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.asarray(vectors / np.where(norms == 0, 1, norms), dtype=np.float32)
