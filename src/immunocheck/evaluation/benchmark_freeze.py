"""Manifesto verificável para o congelamento do benchmark fim a fim."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from immunocheck.evaluation.end_to_end import (
    EndToEndDatasetError,
    EndToEndItem,
    load_end_to_end_items,
    validate_dataset_ready,
)
from immunocheck.evaluation.split_rebalance import class_split_counts

FREEZE_SCHEMA_VERSION = 1


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalized_markdown_bytes(content: bytes) -> bytes:
    """Normaliza somente BOM e finais de linha para publicação reproduzível."""
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]
    return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def build_freeze_manifest(
    items: tuple[EndToEndItem, ...],
    *,
    frozen_at: str,
    corpus_version: str,
    corpus_chunks_sha256: str,
    source_snapshot_sha256: str,
    file_hashes: dict[str, str],
    rebalance: dict[str, Any],
    adjudication: dict[str, Any],
    semantic_audit: dict[str, Any],
) -> dict[str, Any]:
    try:
        date.fromisoformat(frozen_at)
    except ValueError as exc:
        raise EndToEndDatasetError("Data de congelamento inválida.") from exc
    summary = validate_dataset_ready(items)
    stable: dict[str, Any] = {
        "schema_version": FREEZE_SCHEMA_VERSION,
        "purpose": "end_to_end_benchmark_freeze",
        "frozen_at": frozen_at,
        "test_frozen": True,
        "authorization": {
            "actor_code": "project_author",
            "scope": [
                "incorporate_22_human_decisions",
                "apply_approved_family_rebalance",
                "publish_deidentified_review_records",
                "freeze_test_split",
            ],
            "record": "explicit_authorization_in_project_thread",
        },
        "corpus_version": corpus_version,
        "corpus_chunks_sha256": corpus_chunks_sha256,
        "hash_normalization": "UTF-8, CRLF/CR normalized to LF, no BOM",
        "source_snapshot_sha256": source_snapshot_sha256,
        "frozen_dataset_sha256": file_hashes["items.jsonl"],
        "summary": asdict(summary),
        "class_split_counts": class_split_counts(items),
        "rebalance": rebalance,
        "adjudication": adjudication,
        "semantic_audit": semantic_audit,
        "files": [{"path": path, "sha256": digest} for path, digest in sorted(file_hashes.items())],
        "limitations": [
            "benchmark_inteiramente_sintetico",
            "identidade_competencia_e_independencia_humana_nao_certificadas_por_software",
            "triagem_semantica_assistida_por_ia_aceita_pelo_autor_mas_nao_pelo_orientador",
            "moldes_sinteticos_podem_permitir_atalhos_lexicais",
            "teste_nao_deve_ser_usado_para_ajustar_prompt_modelo_limiar_ou_retrieval",
        ],
    }
    stable["freeze_id"] = "sha256:" + sha256_bytes(_canonical_json(stable))
    return stable


def validate_freeze_manifest(
    *,
    root: Path,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or root / "freeze_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EndToEndDatasetError("Manifesto de congelamento ausente ou inválido.") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != FREEZE_SCHEMA_VERSION:
        raise EndToEndDatasetError("Schema de congelamento não suportado.")
    if manifest.get("test_frozen") is not True:
        raise EndToEndDatasetError("O manifesto não declara o teste congelado.")
    if manifest.get("hash_normalization") != "UTF-8, CRLF/CR normalized to LF, no BOM":
        raise EndToEndDatasetError("Política de hash do congelamento inválida.")
    try:
        date.fromisoformat(str(manifest["frozen_at"]))
    except (KeyError, ValueError) as exc:
        raise EndToEndDatasetError("Data de congelamento inválida.") from exc
    freeze_id = manifest.get("freeze_id")
    stable = {key: value for key, value in manifest.items() if key != "freeze_id"}
    if freeze_id != "sha256:" + sha256_bytes(_canonical_json(stable)):
        raise EndToEndDatasetError("Identidade do congelamento inválida.")

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise EndToEndDatasetError("Manifesto de congelamento sem arquivos.")
    seen: set[str] = set()
    for record in files:
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise EndToEndDatasetError("Registro de arquivo inválido no congelamento.")
        relative = Path(str(record["path"]))
        target = (root / relative).resolve()
        if relative.is_absolute() or not target.is_relative_to(root.resolve()):
            raise EndToEndDatasetError("Caminho fora do benchmark no congelamento.")
        if relative.as_posix() in seen:
            raise EndToEndDatasetError("Arquivo duplicado no manifesto de congelamento.")
        seen.add(relative.as_posix())
        try:
            digest = sha256_bytes(normalized_markdown_bytes(target.read_bytes()))
        except OSError as exc:
            raise EndToEndDatasetError(
                f"Arquivo congelado ausente: {relative.as_posix()}."
            ) from exc
        if digest != record["sha256"]:
            raise EndToEndDatasetError(f"Arquivo congelado alterado: {relative.as_posix()}.")

    items = load_end_to_end_items(root / "items.jsonl", require_reviewed=True)
    summary = validate_dataset_ready(items)
    if manifest.get("frozen_dataset_sha256") != sha256_bytes(
        normalized_markdown_bytes((root / "items.jsonl").read_bytes())
    ):
        raise EndToEndDatasetError("Hash do dataset congelado diverge.")
    if manifest.get("summary") != asdict(summary):
        raise EndToEndDatasetError("Resumo do dataset diverge do congelamento.")
    if manifest.get("class_split_counts") != class_split_counts(items):
        raise EndToEndDatasetError("Estratificação diverge do congelamento.")
    if manifest.get("source_snapshot_sha256") != sha256_bytes(
        normalized_markdown_bytes((root / "review_pool.jsonl").read_bytes())
    ):
        raise EndToEndDatasetError("Snapshot primário diverge do congelamento.")
    corpus_manifest_path = root.parents[1] / "corpus/processed/manifest.json"
    try:
        corpus_manifest = json.loads(corpus_manifest_path.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EndToEndDatasetError("Manifesto do corpus congelado está indisponível.") from exc
    if manifest.get("corpus_version") != corpus_manifest.get("corpus_version") or manifest.get(
        "corpus_chunks_sha256"
    ) != corpus_manifest.get("chunks_sha256"):
        raise EndToEndDatasetError("Corpus ativo diverge daquele vinculado ao congelamento.")
    return manifest


def serialize_freeze_manifest(manifest: dict[str, Any]) -> bytes:
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
