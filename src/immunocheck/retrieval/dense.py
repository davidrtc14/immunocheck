from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from functools import cached_property
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from immunocheck.domain.models import Evidence, ExtractedClaim

BGE_M3_MODEL = "BAAI/bge-m3"
BGE_M3_REVISION = "b28ce2a6fcc9c75ef1c0619575d0ec19af760082"
DENSE_INDEX_SCHEMA_VERSION = 1


class DenseIndexError(RuntimeError):
    """Indica inconsistência em embeddings ou no índice denso local."""


class TextEmbedder(Protocol):
    @property
    def dimension(self) -> int: ...

    def encode(self, texts: Sequence[str]) -> NDArray[np.float32]: ...


class SentenceTransformerEmbedder:
    def __init__(
        self,
        *,
        model_name: str = BGE_M3_MODEL,
        revision: str = BGE_M3_REVISION,
        cache_folder: Path | None = None,
        device: str = "cpu",
        batch_size: int = 8,
        local_files_only: bool = False,
        show_progress_bar: bool = False,
    ) -> None:
        if device != "cpu":
            raise ValueError("A configuração da v1 mantém o embedder na CPU.")
        if batch_size <= 0:
            raise ValueError("batch_size deve ser positivo.")
        self.model_name = model_name
        self.revision = revision
        self.cache_folder = cache_folder
        self.device = device
        self.batch_size = batch_size
        self.local_files_only = local_files_only
        self.show_progress_bar = show_progress_bar

    @cached_property
    def _model(self):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            self.model_name,
            device=self.device,
            cache_folder=str(self.cache_folder) if self.cache_folder else None,
            trust_remote_code=False,
            revision=self.revision,
            local_files_only=self.local_files_only,
        )

    @property
    def dimension(self) -> int:
        dimension = self._model.get_embedding_dimension()
        if not isinstance(dimension, int) or dimension <= 0:
            raise DenseIndexError("O modelo não informou uma dimensão de embedding válida.")
        return dimension

    def encode(self, texts: Sequence[str]) -> NDArray[np.float32]:
        normalized_texts = list(texts)
        if not normalized_texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        if any(not isinstance(text, str) or not text.strip() for text in normalized_texts):
            raise ValueError("Todos os textos devem ser strings não vazias.")
        vectors = self._model.encode(
            normalized_texts,
            batch_size=self.batch_size,
            show_progress_bar=self.show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        array = np.asarray(vectors, dtype=np.float32)
        _validate_matrix(array, expected_rows=len(normalized_texts))
        return array


@dataclass(frozen=True, slots=True)
class DenseIndexManifest:
    schema_version: int
    model_name: str
    model_revision: str
    sentence_transformers_version: str
    corpus_sha256: str
    chunk_count: int
    dimension: int
    normalized: bool
    generated_at: str


class DenseIndex:
    def __init__(
        self,
        evidence: Sequence[Evidence],
        vectors: NDArray[np.float32],
    ) -> None:
        if not evidence:
            raise DenseIndexError("O índice denso exige evidências.")
        array = np.asarray(vectors, dtype=np.float32)
        _validate_matrix(array, expected_rows=len(evidence))
        if len({item.chunk_id for item in evidence}) != len(evidence):
            raise DenseIndexError("O índice denso contém chunk_id duplicado.")
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise DenseIndexError("O índice denso contém vetor nulo.")
        self._evidence = tuple(evidence)
        self._vectors = np.ascontiguousarray(array / norms, dtype=np.float32)

    @property
    def dimension(self) -> int:
        return int(self._vectors.shape[1])

    @property
    def vectors(self) -> NDArray[np.float32]:
        return self._vectors.copy()

    @property
    def chunk_ids(self) -> tuple[str, ...]:
        return tuple(item.chunk_id for item in self._evidence)

    def search(
        self,
        query_vector: NDArray[np.float32],
        *,
        top_k: int = 10,
    ) -> tuple[Evidence, ...]:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        query = np.asarray(query_vector, dtype=np.float32)
        if query.ndim == 2 and query.shape[0] == 1:
            query = query[0]
        if query.ndim != 1 or query.shape[0] != self.dimension:
            raise DenseIndexError("O vetor de consulta possui dimensão incompatível.")
        if not np.all(np.isfinite(query)):
            raise DenseIndexError("O vetor de consulta contém valor não finito.")
        norm = float(np.linalg.norm(query))
        if norm == 0:
            raise DenseIndexError("O vetor de consulta é nulo.")
        scores = self._vectors @ (query / norm)
        ranked = sorted(
            enumerate(scores),
            key=lambda item: (-float(item[1]), self._evidence[item[0]].chunk_id),
        )
        return tuple(
            replace(self._evidence[index], retrieval_score=float(score))
            for index, score in ranked[:top_k]
        )


class DenseRetriever:
    def __init__(self, embedder: TextEmbedder, index: DenseIndex, *, top_k: int = 10) -> None:
        if top_k <= 0:
            raise ValueError("top_k deve ser positivo.")
        if embedder.dimension != index.dimension:
            raise DenseIndexError("Embedder e índice possuem dimensões diferentes.")
        self._embedder = embedder
        self._index = index
        self._top_k = top_k

    def retrieve(self, claim: ExtractedClaim) -> Sequence[Evidence]:
        vector = self._embedder.encode((claim.text,))
        return self._index.search(vector, top_k=self._top_k)


def save_dense_index(
    *,
    index: DenseIndex,
    vectors_path: Path,
    manifest_path: Path,
    model_name: str,
    model_revision: str,
    sentence_transformers_version: str,
    corpus_path: Path,
) -> DenseIndexManifest:
    vectors_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_vectors = vectors_path.with_suffix(vectors_path.suffix + ".tmp")
    with temporary_vectors.open("wb") as output:
        np.savez_compressed(
            output,
            vectors=index.vectors,
            chunk_ids=np.asarray(index.chunk_ids),
        )
    temporary_vectors.replace(vectors_path)

    manifest = DenseIndexManifest(
        schema_version=DENSE_INDEX_SCHEMA_VERSION,
        model_name=model_name,
        model_revision=model_revision,
        sentence_transformers_version=sentence_transformers_version,
        corpus_sha256=_sha256_file(corpus_path),
        chunk_count=len(index.chunk_ids),
        dimension=index.dimension,
        normalized=True,
        generated_at=datetime.now(UTC).isoformat(),
    )
    temporary_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    temporary_manifest.write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_manifest.replace(manifest_path)
    return manifest


def load_dense_index(
    *,
    evidence: Sequence[Evidence],
    vectors_path: Path,
    manifest_path: Path,
    corpus_path: Path,
    expected_model_name: str = BGE_M3_MODEL,
    expected_model_revision: str = BGE_M3_REVISION,
) -> tuple[DenseIndex, DenseIndexManifest]:
    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = DenseIndexManifest(**manifest_data)
        with np.load(vectors_path, allow_pickle=False) as artifact:
            vectors = np.asarray(artifact["vectors"], dtype=np.float32)
            chunk_ids = tuple(str(item) for item in artifact["chunk_ids"].tolist())
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DenseIndexError("Não foi possível carregar o índice denso.") from exc

    if manifest.schema_version != DENSE_INDEX_SCHEMA_VERSION:
        raise DenseIndexError("Versão incompatível do índice denso.")
    if (
        manifest.model_name != expected_model_name
        or manifest.model_revision != expected_model_revision
    ):
        raise DenseIndexError("O índice foi gerado com outro modelo ou revisão.")
    if not manifest.normalized:
        raise DenseIndexError("O índice denso precisa conter vetores normalizados.")
    if manifest.corpus_sha256 != _sha256_file(corpus_path):
        raise DenseIndexError("O corpus mudou depois da geração do índice denso.")
    _validate_matrix(vectors, expected_rows=len(chunk_ids))
    if manifest.chunk_count != len(chunk_ids) or manifest.dimension != vectors.shape[1]:
        raise DenseIndexError("Manifesto e vetores do índice denso divergem.")

    evidence_by_id = {item.chunk_id: item for item in evidence}
    if len(evidence_by_id) != len(evidence):
        raise DenseIndexError("As evidências contêm chunk_id duplicado.")
    try:
        ordered_evidence = tuple(evidence_by_id[chunk_id] for chunk_id in chunk_ids)
    except KeyError as exc:
        raise DenseIndexError("O índice referencia um trecho ausente do corpus.") from exc
    return DenseIndex(ordered_evidence, vectors), manifest


def _validate_matrix(array: NDArray[np.float32], *, expected_rows: int) -> None:
    if array.ndim != 2 or array.shape[0] != expected_rows or array.shape[1] <= 0:
        raise DenseIndexError("A matriz de embeddings possui formato inválido.")
    if not np.all(np.isfinite(array)):
        raise DenseIndexError("A matriz de embeddings contém valores não finitos.")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise DenseIndexError(f"Não foi possível calcular o hash de {path.name}.") from exc
    return digest.hexdigest()
