from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from immunocheck.application.text_components import ModelOutputError
from immunocheck.bootstrap import DEFAULT_CORPUS_PATH, build_text_pipeline
from immunocheck.domain.input_policy import InvalidSubmissionError
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict
from immunocheck.infrastructure.ollama import OllamaError
from immunocheck.retrieval.pilot_corpus import CorpusLoadError

VERDICT_LABELS = {
    Verdict.SUPPORTED: "SUSTENTADA",
    Verdict.REFUTED: "REFUTADA",
    Verdict.MISLEADING: "ENGANOSA",
    Verdict.INSUFFICIENT_EVIDENCE: "EVIDÊNCIA INSUFICIENTE",
}

MEDICAL_DISCLAIMER = (
    "Esta análise compara uma alegação com fontes documentais e não substitui "
    "orientação de um profissional de saúde."
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    text = " ".join(args.text).strip()
    if not text:
        parser.error("informe a alegação textual entre aspas")

    started_at = time.perf_counter()
    try:
        pipeline = build_text_pipeline(
            corpus_path=args.corpus,
            model=args.model,
            base_url=args.ollama_url,
            top_k=args.top_k,
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


def format_result(result: FactCheckResult, *, elapsed_seconds: float) -> str:
    lines = [
        f"VEREDITO: {VERDICT_LABELS[result.verdict]}",
        f"ALEGAÇÃO ANALISADA: {result.claim or 'não identificada'}",
        f"EXPLICAÇÃO: {result.explanation}",
    ]
    if result.correct_fact:
        lines.append(f"FATO CORRETO: {result.correct_fact}")
    if result.omitted_or_distorted:
        lines.append(f"OMISSÃO OU DISTORÇÃO: {result.omitted_or_distorted}")
    if result.sources:
        lines.append("FONTES:")
        for position, source in enumerate(result.sources, start=1):
            details = [source.source_name, source.document_title]
            if source.publication_date:
                details.append(source.publication_date)
            if source.page:
                details.append(f"p. {source.page}")
            lines.append(f"  [{position}] {' — '.join(details)}")
            lines.append(f"      {source.url}")
    else:
        lines.append("FONTES: nenhuma fonte suficiente para sustentar uma conclusão.")
    lines.extend(
        (
            f"AVISO: {MEDICAL_DISCLAIMER}",
            f"TEMPO TOTAL: {elapsed_seconds:.2f} s",
        )
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="immunocheck",
        description="Protótipo local para verificar alegações sobre vacinação humana.",
    )
    parser.add_argument("text", nargs="*", help="alegação textual a verificar")
    parser.add_argument("--model", default=None, help="modelo local configurado no Ollama")
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
    parser.add_argument("--top-k", type=int, default=6, help="quantidade de evidências recuperadas")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
