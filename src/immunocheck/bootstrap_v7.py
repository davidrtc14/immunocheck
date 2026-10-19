"""Montagem da v7 (ADR-054) a partir da `v5_fixed`, com as candidatas ligadas por nome.

Fica fora de `bootstrap.py`, que está congelado pela Fase 18. Candidatas disponíveis:
- `C1`: relação de enquadramento `PARTIAL` e agregação da v7.
- `C2`: cada evidência vai ao juiz com o fim do chunk anterior e o começo do seguinte.
- `C4`: queda para a v3 quando a decomposição falha duas vezes.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable
from typing import Any

from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.application.v7_fallback import DecompositionFallbackPipeline
from immunocheck.application.v7_verdict import FramingPropositionJudge, V7FactCheckPipeline
from immunocheck.bootstrap import (
    DEFAULT_CORPUS_PATH,
    build_routed_text_pipeline,
    build_v5_text_pipeline,
)
from immunocheck.retrieval.neighbor_context import NeighborContextRetriever
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

CANDIDATES = ("C1", "C2", "C4")


def build_v7_text_pipeline(
    candidates: Iterable[str],
    *,
    model: str | None = None,
    trace_sink: Callable[[dict[str, Any]], None] | None = None,
) -> V7FactCheckPipeline | DecompositionFallbackPipeline:
    chosen = set(candidates)
    unknown = chosen - set(CANDIDATES)
    if unknown:
        raise ValueError(f"Candidatas desconhecidas: {sorted(unknown)}")
    base = build_v5_text_pipeline(
        model=model, multi_query=True, reranker=False, think=False, trace_sink=trace_sink
    )
    client = base.judge.client
    tokens = base.judge.max_output_tokens
    judge = (
        FramingPropositionJudge(client, tokens)
        if "C1" in chosen
        else TolerantPropositionJudge(client, tokens)
    )
    fields = {field.name: getattr(base, field.name) for field in dataclasses.fields(base)}
    if "C2" in chosen:
        corpus = load_evidence_jsonl(DEFAULT_CORPUS_PATH)
        fields["retriever"] = NeighborContextRetriever(base.retriever, corpus)
    pipeline = V7FactCheckPipeline(**(fields | {"judge": judge}))
    if "C4" in chosen:
        return DecompositionFallbackPipeline(
            pipeline, build_routed_text_pipeline, trace_sink=trace_sink
        )
    return pipeline
