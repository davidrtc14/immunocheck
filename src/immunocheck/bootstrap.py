from __future__ import annotations

import os
from pathlib import Path

from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.ports import ContentNormalizer
from immunocheck.application.text_components import (
    FACTUAL_VERIFICATION_SYSTEM_PROMPT_V3,
    GuardedFaithfulnessVerifier,
    LLMClaimExtractor,
    LLMConclusiveVerdictGenerator,
    LLMEvidenceSufficiencyAssessor,
    LLMFaithfulnessVerifier,
    LLMVerdictGenerator,
    TextNormalizer,
)
from immunocheck.infrastructure.ocr import TesseractOCR
from immunocheck.infrastructure.ollama import OllamaStructuredClient
from immunocheck.infrastructure.web_content import SafeLinkTextExtractor
from immunocheck.retrieval.dense import (
    DenseRetriever,
    SentenceTransformerEmbedder,
    load_dense_index,
)
from immunocheck.retrieval.pilot_corpus import (
    PilotCorpusBM25Retriever,
    load_evidence_jsonl,
)
from immunocheck.retrieval.rrf import HybridRetriever

PROJECT_ROOT = Path(__file__).parents[2]
DEFAULT_CORPUS_PATH = PROJECT_ROOT / "corpus" / "processed" / "chunks.jsonl"
DEFAULT_DENSE_VECTORS_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.npz"
DEFAULT_DENSE_MANIFEST_PATH = PROJECT_ROOT / "corpus" / "processed" / "dense_bge_m3.json"
DEFAULT_MODEL_CACHE = PROJECT_ROOT / "models"
RRF_INPUT_DEPTH = 60
RRF_RANK_CONSTANT = 60


def build_text_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline:
    return _build_pipeline(
        normalizer=TextNormalizer(),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        separated_decision=False,
    )


def build_multimodal_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline:
    return _build_pipeline(
        normalizer=MultimodalNormalizer(
            image_extractor=TesseractOCR.from_environment(),
            link_extractor=SafeLinkTextExtractor(),
        ),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        separated_decision=False,
    )


def build_refinement_text_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline:
    """Monta a candidata v2 sem alterar a configuração de produção da v1."""
    return _build_pipeline(
        normalizer=TextNormalizer(),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        separated_decision=True,
    )


def build_refinement_multimodal_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline:
    """Monta a candidata multimodal v2, ainda sem promovê-la ao bot."""
    return _build_pipeline(
        normalizer=MultimodalNormalizer(
            image_extractor=TesseractOCR.from_environment(),
            link_extractor=SafeLinkTextExtractor(),
        ),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
        separated_decision=True,
    )


def _build_pipeline(
    *,
    normalizer: ContentNormalizer,
    corpus_path: Path,
    model: str | None,
    base_url: str | None,
    top_k: int,
    retrieval_mode: str | None,
    separated_decision: bool,
) -> FactCheckPipeline:
    client = OllamaStructuredClient(
        model=model or os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )
    sufficiency_assessor, generator, verifier = _build_decision_components(
        client, separated_decision=separated_decision
    )
    return FactCheckPipeline(
        normalizer=normalizer,
        claim_extractor=LLMClaimExtractor(client),
        retriever=_build_retriever(
            corpus_path=corpus_path,
            top_k=top_k,
            retrieval_mode=retrieval_mode or os.getenv("RETRIEVAL_MODE", "dense"),
        ),
        generator=generator,
        verifier=verifier,
        sufficiency_assessor=sufficiency_assessor,
    )


def _build_decision_components(client, *, separated_decision: bool):
    if not separated_decision:
        return (
            None,
            LLMVerdictGenerator(client),
            GuardedFaithfulnessVerifier(LLMFaithfulnessVerifier(client)),
        )
    return (
        LLMEvidenceSufficiencyAssessor(client),
        LLMConclusiveVerdictGenerator(client),
        GuardedFaithfulnessVerifier(
            LLMFaithfulnessVerifier(
                client,
                system_prompt=FACTUAL_VERIFICATION_SYSTEM_PROMPT_V3,
                map_nonliteral_to_full_draft=True,
            )
        ),
    )


def _build_retriever(*, corpus_path: Path, top_k: int, retrieval_mode: str):
    mode = retrieval_mode.strip().lower()
    if mode == "bm25":
        return PilotCorpusBM25Retriever.from_jsonl(corpus_path, top_k=top_k)
    if mode not in {"dense", "hybrid"}:
        raise ValueError("RETRIEVAL_MODE deve ser 'dense', 'hybrid' ou 'bm25'.")

    evidence = load_evidence_jsonl(corpus_path)
    bm25 = PilotCorpusBM25Retriever(evidence, top_k=RRF_INPUT_DEPTH)
    vectors_path = corpus_path.parent / DEFAULT_DENSE_VECTORS_PATH.name
    manifest_path = corpus_path.parent / DEFAULT_DENSE_MANIFEST_PATH.name
    dense_index, _ = load_dense_index(
        evidence=evidence,
        vectors_path=vectors_path,
        manifest_path=manifest_path,
        corpus_path=corpus_path,
    )
    embedder = SentenceTransformerEmbedder(
        cache_folder=DEFAULT_MODEL_CACHE,
        device="cpu",
        local_files_only=True,
    )
    dense = DenseRetriever(
        embedder,
        dense_index,
        top_k=top_k if mode == "dense" else RRF_INPUT_DEPTH,
    )
    if mode == "dense":
        return dense
    return HybridRetriever(
        (bm25, dense),
        top_k=top_k,
        rank_constant=RRF_RANK_CONSTANT,
    )
