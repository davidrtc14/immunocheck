from __future__ import annotations

import os
from pathlib import Path

from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.text_components import (
    GuardedFaithfulnessVerifier,
    LLMClaimExtractor,
    LLMFaithfulnessVerifier,
    LLMVerdictGenerator,
    TextNormalizer,
)
from immunocheck.infrastructure.ollama import OllamaStructuredClient
from immunocheck.retrieval.pilot_corpus import PilotCorpusBM25Retriever

PROJECT_ROOT = Path(__file__).parents[2]
DEFAULT_CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"


def build_text_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
) -> FactCheckPipeline:
    client = OllamaStructuredClient(
        model=model or os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )
    return FactCheckPipeline(
        normalizer=TextNormalizer(),
        claim_extractor=LLMClaimExtractor(client),
        retriever=PilotCorpusBM25Retriever.from_jsonl(corpus_path, top_k=top_k),
        generator=LLMVerdictGenerator(client),
        verifier=GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)),
    )
