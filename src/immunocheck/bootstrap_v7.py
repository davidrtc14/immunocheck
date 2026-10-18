"""Montagem da v7 (ADR-054) a partir da `v5_fixed`, com as candidatas ligadas por nome.

Fica fora de `bootstrap.py`, que está congelado pela Fase 18. Candidatas disponíveis:
- `C1`: relação de enquadramento `PARTIAL` e agregação da v7.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable
from typing import Any

from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.application.v7_verdict import FramingPropositionJudge, V7FactCheckPipeline
from immunocheck.bootstrap import build_v5_text_pipeline

CANDIDATES = ("C1",)


def build_v7_text_pipeline(
    candidates: Iterable[str],
    *,
    model: str | None = None,
    trace_sink: Callable[[dict[str, Any]], None] | None = None,
) -> V7FactCheckPipeline:
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
    return V7FactCheckPipeline(**(fields | {"judge": judge}))
