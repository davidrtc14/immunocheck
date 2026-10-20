"""Montagem da v7 (ADR-054) a partir da `v5_fixed`, com as candidatas ligadas por nome.

Fica fora de `bootstrap.py`, que está congelado pela Fase 18. Candidatas disponíveis:
- `C1`: relação de enquadramento `PARTIAL` e agregação da v7.
- `C2`: cada evidência vai ao juiz com o fim do chunk anterior e o começo do seguinte.
- `C3`: `qwen3.6` só no juiz; decomposição e explicação continuam com o modelo base.
- `C3b`: `qwen3.6` no pipeline inteiro, sem troca de modelo (Adendo 2 do protocolo).
- `C4`: queda para a v3 quando a decomposição falha duas vezes.
- `C5`: voto de três juízes (temperatura 0,3, sementes 42, 43 e 44) por proposição.
"""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Callable, Iterable
from typing import Any

from immunocheck.application.cascade import SupportedVerificationCascade
from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.application.v7_fallback import DecompositionFallbackPipeline
from immunocheck.application.v7_verdict import FramingPropositionJudge, V7FactCheckPipeline
from immunocheck.application.v7_vote import ConsistencyVoteJudge
from immunocheck.bootstrap import (
    DEFAULT_CORPUS_PATH,
    _build_llm_client,
    build_routed_text_pipeline,
    build_v5_text_pipeline,
)
from immunocheck.infrastructure.context_budget import ContextBudgetClient
from immunocheck.infrastructure.ollama_seeded import SeededOllamaClient
from immunocheck.retrieval.neighbor_context import NeighborContextRetriever
from immunocheck.retrieval.pilot_corpus import load_evidence_jsonl

CANDIDATES = ("C1", "C2", "C3", "C3b", "C4", "C5")
C5_SEEDS = (42, 43, 44)
C5_TEMPERATURE = 0.3
C3_JUDGE_MODEL = "qwen3.6:latest"


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
        model=C3_JUDGE_MODEL if "C3b" in chosen else model,
        multi_query=True,
        reranker=False,
        think=False,
        trace_sink=trace_sink,
    )
    client = (
        _build_llm_client(model=C3_JUDGE_MODEL, base_url=None)
        if "C3" in chosen
        else base.judge.client
    )
    tokens = base.judge.max_output_tokens
    judge_class = FramingPropositionJudge if "C1" in chosen else TolerantPropositionJudge
    judge = judge_class(client, tokens)
    if "C5" in chosen:
        judge_model = C3_JUDGE_MODEL if chosen & {"C3", "C3b"} else _base_model(model)
        judge = ConsistencyVoteJudge(
            tuple(
                judge_class(
                    ContextBudgetClient(
                        SeededOllamaClient(model=judge_model, seed=seed, temperature=C5_TEMPERATURE)
                    ),
                    tokens,
                )
                for seed in C5_SEEDS
            )
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


def _base_model(model: str | None) -> str:
    return model or os.getenv("OLLAMA_MODEL", "qwen3:8b")


def build_cascade_pipeline(
    *, trace_sink: Callable[[dict[str, Any]], None] | None = None
) -> SupportedVerificationCascade:
    """C6 (ADR-055): v3 primeiro; a `v5_fixed`, montada como na Fase 18, confere os `SUPPORTED`."""

    verifier_traces: list[dict[str, Any]] = []
    v5 = build_v5_text_pipeline(
        multi_query=True, reranker=False, think=False, trace_sink=verifier_traces.append
    )
    tolerant = TolerantPropositionJudge(v5.judge.client, v5.judge.max_output_tokens)
    return SupportedVerificationCascade(
        primary=build_routed_text_pipeline(),
        verifier=dataclasses.replace(v5, judge=tolerant),
        trace_sink=trace_sink,
        verifier_traces=verifier_traces,
    )
