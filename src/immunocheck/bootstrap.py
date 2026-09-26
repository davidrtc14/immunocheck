from __future__ import annotations

import os
from pathlib import Path

from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.application.pipeline import FactCheckPipeline
from immunocheck.application.ports import ContentNormalizer
from immunocheck.application.routed_pipeline import RoutedFactCheckPipeline
from immunocheck.application.text_components import (
    FACTUAL_VERIFICATION_SYSTEM_PROMPT_V3,
    GuardedFaithfulnessVerifier,
    LLMCitationSelector,
    LLMClaimExtractor,
    LLMClaimRouteAnalyzer,
    LLMConclusiveVerdictGenerator,
    LLMEvidenceSufficiencyAssessor,
    LLMFaithfulnessVerifier,
    LLMRelationVerdictGenerator,
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
V3_RETRIEVAL_TOP_K = 15


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


def build_routed_text_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
) -> RoutedFactCheckPipeline:
    """Monta a candidata v3 confirmada com entrada textual."""
    return _build_routed_pipeline(
        normalizer=TextNormalizer(),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
    )


def build_routed_multimodal_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
) -> RoutedFactCheckPipeline:
    """Monta a candidata v3 confirmada com texto, imagem e link."""
    return _build_routed_pipeline(
        normalizer=MultimodalNormalizer(
            image_extractor=TesseractOCR.from_environment(),
            link_extractor=SafeLinkTextExtractor(),
        ),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
    )


def build_configured_text_pipeline(
    *,
    pipeline_version: str | None = None,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline | RoutedFactCheckPipeline:
    version = _pipeline_version(pipeline_version)
    if version == "v3":
        return build_routed_text_pipeline(
            corpus_path=corpus_path,
            model=model,
            base_url=base_url,
        )
    return build_text_pipeline(
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
    )


def build_configured_multimodal_pipeline(
    *,
    pipeline_version: str | None = None,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    top_k: int = 6,
    retrieval_mode: str | None = None,
) -> FactCheckPipeline | RoutedFactCheckPipeline:
    version = _pipeline_version(pipeline_version)
    if version == "v3":
        return build_routed_multimodal_pipeline(
            corpus_path=corpus_path,
            model=model,
            base_url=base_url,
        )
    return build_multimodal_pipeline(
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        top_k=top_k,
        retrieval_mode=retrieval_mode,
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


def _build_routed_pipeline(
    *,
    normalizer: ContentNormalizer,
    corpus_path: Path,
    model: str | None,
    base_url: str | None,
) -> RoutedFactCheckPipeline:
    client = OllamaStructuredClient(
        model=model or os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )
    corpus = load_evidence_jsonl(corpus_path)
    return RoutedFactCheckPipeline(
        normalizer=normalizer,
        claim_extractor=LLMClaimExtractor(client),
        retriever=_build_retriever(
            corpus_path=corpus_path,
            top_k=V3_RETRIEVAL_TOP_K,
            retrieval_mode="dense",
        ),
        direct_generator=LLMVerdictGenerator(client),
        relation_generator=LLMRelationVerdictGenerator(client),
        router=LLMClaimRouteAnalyzer(client),
        citation_selector=LLMCitationSelector(client),
        corpus=corpus,
    )


def _pipeline_version(value: str | None) -> str:
    version = (value or os.getenv("PIPELINE_VERSION", "v3")).strip().lower()
    if version not in {"v1", "v3"}:
        raise ValueError("PIPELINE_VERSION deve ser 'v1' ou 'v3'.")
    return version


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
