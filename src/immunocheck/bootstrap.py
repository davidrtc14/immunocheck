from __future__ import annotations

import json
import os
from pathlib import Path

from immunocheck.application.abstention import (
    AbstainingPipeline,
    AbstentionThresholds,
    RecordingClaimExtractor,
    RecordingRetriever,
    RecordingRouter,
    SignalRecorder,
)
from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.application.grounding import GroundedVerdictGenerator
from immunocheck.application.misleading import (
    FEW_SHOT_BLOCK,
    CombinedVerdictGenerator,
    PromptAugmentingClient,
    ResilientVerdictGenerator,
)
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
from immunocheck.infrastructure.context_budget import ContextBudgetClient
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
V4_THRESHOLDS_PATH = PROJECT_ROOT / "evaluation" / "refinement_v4" / "thresholds.json"


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


def build_v4_text_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    grounded: bool | None = None,
    thresholds: AbstentionThresholds | None = None,
    d4: bool = False,
) -> AbstainingPipeline:
    """Monta a v4 opt-in (ancoragem D1 + abstenção calibrada D2) com entrada textual."""
    return _build_v4_pipeline(
        normalizer=TextNormalizer(),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        grounded=grounded,
        thresholds=thresholds,
        d4=d4,
    )


def build_v4_multimodal_pipeline(
    *,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    model: str | None = None,
    base_url: str | None = None,
    grounded: bool | None = None,
    thresholds: AbstentionThresholds | None = None,
    d4: bool = False,
) -> AbstainingPipeline:
    return _build_v4_pipeline(
        normalizer=MultimodalNormalizer(
            image_extractor=TesseractOCR.from_environment(),
            link_extractor=SafeLinkTextExtractor(),
        ),
        corpus_path=corpus_path,
        model=model,
        base_url=base_url,
        grounded=grounded,
        thresholds=thresholds,
        d4=d4,
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
    version = resolve_pipeline_version(pipeline_version)
    if version == "v4":
        return build_v4_text_pipeline(corpus_path=corpus_path, model=model, base_url=base_url)
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
    version = resolve_pipeline_version(pipeline_version)
    if version == "v4":
        return build_v4_multimodal_pipeline(corpus_path=corpus_path, model=model, base_url=base_url)
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
    client = _build_llm_client(model=model, base_url=base_url)
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
    client = _build_llm_client(model=model, base_url=base_url)
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


def _build_llm_client(*, model: str | None, base_url: str | None) -> ContextBudgetClient:
    ollama = OllamaStructuredClient(
        model=model or os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )
    return ContextBudgetClient(ollama, context_tokens=ollama.context_tokens)


def _build_v4_pipeline(
    *,
    normalizer: ContentNormalizer,
    corpus_path: Path,
    model: str | None,
    base_url: str | None,
    grounded: bool | None,
    thresholds: AbstentionThresholds | None,
    d4: bool = False,
) -> AbstainingPipeline:
    if grounded is None:
        grounded = _v4_grounded_default()
    client = _build_llm_client(model=model, base_url=base_url)
    corpus = load_evidence_jsonl(corpus_path)
    recorder = SignalRecorder()
    if grounded:
        direct = GroundedVerdictGenerator(client, LLMVerdictGenerator)
        relation = GroundedVerdictGenerator(client, LLMRelationVerdictGenerator)
    else:
        direct, relation = LLMVerdictGenerator(client), LLMRelationVerdictGenerator(client)
    if d4:
        few_shot = GroundedVerdictGenerator(
            client,
            lambda capture: LLMRelationVerdictGenerator(
                PromptAugmentingClient(capture, FEW_SHOT_BLOCK)
            ),
        )
        direct = ResilientVerdictGenerator(
            CombinedVerdictGenerator(direct, few_shot), recorder
        )
        relation = ResilientVerdictGenerator(few_shot, recorder)
    inner = RoutedFactCheckPipeline(
        normalizer=normalizer,
        claim_extractor=RecordingClaimExtractor(LLMClaimExtractor(client), recorder),
        retriever=RecordingRetriever(
            _build_retriever(
                corpus_path=corpus_path,
                top_k=V3_RETRIEVAL_TOP_K,
                retrieval_mode="dense",
            ),
            recorder,
        ),
        direct_generator=direct,
        relation_generator=relation,
        router=RecordingRouter(LLMClaimRouteAnalyzer(client), recorder),
        citation_selector=LLMCitationSelector(client),
        corpus=corpus,
    )
    return AbstainingPipeline(
        inner=inner,
        recorder=recorder,
        thresholds=thresholds
        if thresholds is not None
        else AbstentionThresholds.load(V4_THRESHOLDS_PATH),
    )


def _v4_grounded_default() -> bool:
    """A ancoragem D1 só entra por padrão se a calibração registrada a adotou."""
    if not V4_THRESHOLDS_PATH.is_file():
        return False
    data = json.loads(V4_THRESHOLDS_PATH.read_text(encoding="utf-8"))
    return data.get("base_condition") == "v4_grounded"


def resolve_pipeline_version(value: str | None) -> str:
    version = (value or os.getenv("PIPELINE_VERSION", "v3")).strip().lower()
    if version not in {"v1", "v3", "v4"}:
        raise ValueError("PIPELINE_VERSION deve ser 'v1', 'v3' ou 'v4'.")
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
