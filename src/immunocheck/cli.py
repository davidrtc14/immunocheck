from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from immunocheck.application.text_components import ModelOutputError
from immunocheck.bootstrap import (
    DEFAULT_CORPUS_PATH,
    build_configured_text_pipeline,
    resolve_pipeline_version,
)
from immunocheck.domain.input_policy import InvalidSubmissionError
from immunocheck.domain.models import ContentKind, ContentSubmission
from immunocheck.infrastructure.ollama import OllamaError
from immunocheck.presentation import format_result
from immunocheck.retrieval.pilot_corpus import CorpusLoadError


DEFAULT_V1_TOP_K = 6


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    text = " ".join(args.text).strip()
    if not text:
        parser.error("informe a alegação textual entre aspas")

    started_at = time.perf_counter()
    try:
        if args.top_k is not None and resolve_pipeline_version(args.pipeline_version) == "v3":
            print(
                "Aviso: --top-k é ignorado na v3, que usa profundidade fixa (top 15 congelado).",
                file=sys.stderr,
            )
        pipeline = build_configured_text_pipeline(
            pipeline_version=args.pipeline_version,
            corpus_path=args.corpus,
            model=args.model,
            base_url=args.ollama_url,
            top_k=args.top_k if args.top_k is not None else DEFAULT_V1_TOP_K,
        )
        result = pipeline.run(ContentSubmission(kind=ContentKind.TEXT, text=text))
    except InvalidSubmissionError as exc:
        print(f"Entrada inválida: {exc}", file=sys.stderr)
        return 2
    except (CorpusLoadError, OllamaError, ModelOutputError) as exc:
        print(f"Não foi possível concluir a análise: {exc}", file=sys.stderr)
        return 3

    print(format_result(result, elapsed_seconds=time.perf_counter() - started_at))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="immunocheck",
        description="Protótipo local para verificar alegações sobre vacinação humana.",
    )
    parser.add_argument("text", nargs="*", help="alegação textual a verificar")
    parser.add_argument("--model", default=None, help="modelo local configurado no Ollama")
    parser.add_argument(
        "--pipeline-version",
        choices=("v1", "v3"),
        default=None,
        help="pipeline local (padrão: PIPELINE_VERSION ou v3)",
    )
    parser.add_argument(
        "--ollama-url",
        default=None,
        help="URL local do Ollama (localhost ou endereço de loopback)",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS_PATH,
        help="arquivo JSONL produzido pela construção do corpus",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help=f"evidências recuperadas pela v1 (padrão {DEFAULT_V1_TOP_K}); ignorado na v3",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
