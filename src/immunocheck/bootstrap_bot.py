"""Montagem padrão do bot e da CLI depois da ADR-055: a cascata C6 vira a `v7`, nova versão padrão.

`bootstrap.py`, `bootstrap_v7.py` e `cascade.py` estão congelados (Fases 18 e 20), então a escolha da
versão fica aqui. `PIPELINE_VERSION` aceita `v1`, `v3`, `v4`, `v5` e `v7` (padrão). As versões antigas
continuam montadas por `bootstrap.py`, sem mudança; a `v7` combina a v3 e a `v5_fixed` como na
execução única da Fase 20: a v3 responde e, só quando ela sustenta a alegação, a `v5_fixed` verifica.

Com imagem ou link, as duas etapas compartilham uma única normalização (OCR ou download), descartada
ao fim de cada requisição.
"""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from immunocheck.application.cascade import SupportedVerificationCascade
from immunocheck.application.shared_normalizer import ClearingRunner, SharedNormalizer
from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.bootstrap import (
    DEFAULT_CORPUS_PATH,
    build_configured_multimodal_pipeline,
    build_configured_text_pipeline,
    build_routed_multimodal_pipeline,
    build_routed_text_pipeline,
    build_understanding_normalizer,
    build_v5_multimodal_pipeline,
    build_v5_text_pipeline,
    resolve_extraction_version,
)

PIPELINE_VERSIONS = ("v1", "v3", "v4", "v5", "v7")
DEFAULT_PIPELINE_VERSION = "v7"
FIXED_DEPTH_VERSIONS = frozenset({"v3", "v4", "v5", "v7"})


def resolve_pipeline_version(value: str | None = None) -> str:
    version = (value or os.getenv("PIPELINE_VERSION", DEFAULT_PIPELINE_VERSION)).strip().lower()
    if version not in PIPELINE_VERSIONS:
        raise ValueError(f"PIPELINE_VERSION deve ser uma de: {', '.join(PIPELINE_VERSIONS)}.")
    return version


def _tolerant(pipeline):
    """A `v5_fixed` da Fase 18: v5 com várias consultas, sem reranker e com o juiz tolerante."""

    judge = TolerantPropositionJudge(pipeline.judge.client, pipeline.judge.max_output_tokens)
    return dataclasses.replace(pipeline, judge=judge)


def build_bot_text_pipeline(
    *,
    pipeline_version: str | None = None,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
):
    version = resolve_pipeline_version(pipeline_version)
    if version != "v7":
        return build_configured_text_pipeline(
            pipeline_version=version,
            corpus_path=corpus_path,
            model=model,
            base_url=base_url,
            top_k=top_k,
        )
    return SupportedVerificationCascade(
        primary=build_routed_text_pipeline(corpus_path=corpus_path, model=model, base_url=base_url),
        verifier=_tolerant(
            build_v5_text_pipeline(corpus_path=corpus_path, model=model, base_url=base_url)
        ),
    )


def build_bot_multimodal_pipeline(
    *,
    pipeline_version: str | None = None,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    extraction_version: str | None = None,
):
    version = resolve_pipeline_version(pipeline_version)
    if version != "v7":
        return build_configured_multimodal_pipeline(
            pipeline_version=version,
            corpus_path=corpus_path,
            model=model,
            base_url=base_url,
            extraction_version=extraction_version,
        )
    primary = build_routed_multimodal_pipeline(
        corpus_path=corpus_path, model=model, base_url=base_url
    )
    normalizer = (
        build_understanding_normalizer(base_url=base_url)
        if resolve_extraction_version(extraction_version) == "v2"
        else primary.normalizer
    )
    shared = SharedNormalizer(normalizer)
    verifier = build_v5_multimodal_pipeline(corpus_path=corpus_path, model=model, base_url=base_url)
    cascade = SupportedVerificationCascade(
        primary=dataclasses.replace(primary, normalizer=shared),
        verifier=_tolerant(dataclasses.replace(verifier, normalizer=shared)),
    )
    return ClearingRunner(cascade, shared)
