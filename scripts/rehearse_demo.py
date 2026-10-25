"""Ensaia localmente o roteiro de demonstração sem acessar o Telegram real."""

from __future__ import annotations

import argparse
import io
import json
import os
import platform
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.bootstrap import build_configured_multimodal_pipeline
from immunocheck.infrastructure.ocr import TesseractOCR
from immunocheck.infrastructure.web_content import FetchedResource, SafeLinkTextExtractor
from immunocheck.telegram import (
    PROCESSING_MESSAGE,
    UNSUPPORTED_INPUT_MESSAGE,
    TelegramUpdateHandler,
)

REPOSITORY = Path(__file__).resolve().parents[1]
FINAL_TEST = REPOSITORY / "evaluation/results/test/final_test.json"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/demo/automated_rehearsal.json"
DEMO_URL = "https://demo.invalid/boletim-vacinacao"
REQUIRED_RESPONSE_SECTIONS = (
    "📖 EXPLICAÇÃO:",
    "📝 ALEGAÇÃO ANALISADA:",
    "📚 FONTES",
    "ℹ️ AVISO:",
    "⏱️ TEMPO TOTAL:",
)


@dataclass(slots=True)
class DemoClient:
    image_data: bytes
    messages: list[tuple[int, str]] = field(default_factory=list)
    events: list[str] = field(default_factory=list)

    def send_message(self, chat_id: int, text: str) -> None:
        self.events.append("send")
        self.messages.append((chat_id, text))

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes:
        if file_id != "synthetic-demo-image" or len(self.image_data) > maximum_bytes:
            raise AssertionError("Descritor inesperado no ensaio de imagem.")
        self.events.append("download")
        return self.image_data

    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict, ...]:
        del offset, timeout_seconds
        return ()


@dataclass(frozen=True, slots=True)
class DemoFetcher:
    resource: FetchedResource

    def fetch(self, url: str) -> FetchedResource:
        if url != DEMO_URL:
            raise AssertionError("URL inesperada no ensaio controlado.")
        return self.resource


def main() -> None:
    parser = argparse.ArgumentParser(description="Ensaio local automatizado da demonstração.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pipeline-version", choices=("v1", "v3"), default="v1")
    args = parser.parse_args()
    output_path = args.output.resolve()
    if output_path.exists():
        parser.error("O ensaio registrado já existe; use outro caminho para uma réplica.")

    final_test = json.loads(FINAL_TEST.read_text("utf-8"))
    pipeline = build_configured_multimodal_pipeline(
        pipeline_version=args.pipeline_version,
        model=str(final_test["model"]),
        top_k=int(final_test["configuration"]["top_k"]),
        retrieval_mode="dense",
    )
    image_data = _demo_image()
    client = DemoClient(image_data=image_data)
    handler = TelegramUpdateHandler(client=client, pipeline=pipeline)

    cases: list[dict[str, object]] = []
    cases.append(
        _run_case(
            "text",
            handler,
            client,
            {
                "update_id": 1,
                "message": {
                    "chat": {"id": 10_001},
                    "text": "A vacina triplice viral causa autismo.",
                },
            },
        )
    )
    cases.append(
        _run_case(
            "image",
            handler,
            client,
            {
                "update_id": 2,
                "message": {
                    "chat": {"id": 10_002},
                    "document": {
                        "file_id": "synthetic-demo-image",
                        "file_size": len(image_data),
                        "mime_type": "image/png",
                    },
                },
            },
        )
    )

    html = (
        "<html><head><title>Boletim de vacinação</title></head><body><main>"
        "<p>A vacina contra influenza provoca a própria gripe.</p>"
        "</main></body></html>"
    ).encode()
    pipeline.normalizer = MultimodalNormalizer(
        TesseractOCR.from_environment(),
        SafeLinkTextExtractor(
            fetcher=DemoFetcher(FetchedResource(DEMO_URL, "text/html; charset=utf-8", html))
        ),  # type: ignore[arg-type]
    )
    cases.append(
        _run_case(
            "link_controlled",
            handler,
            client,
            {
                "update_id": 3,
                "message": {"chat": {"id": 10_003}, "text": DEMO_URL},
            },
        )
    )
    cases.append(
        _run_rejection_case(
            handler,
            client,
            {
                "update_id": 4,
                "message": {"chat": {"id": 10_004}, "video": {"file_id": "ignored"}},
            },
        )
    )

    report = {
        "schema_version": 1,
        "purpose": "automated_local_demo_rehearsal_not_quality_evaluation",
        "pipeline_version": args.pipeline_version,
        "executed_at": datetime.now(UTC).isoformat(),
        "current_commit": _git_head(),
        "final_quality_candidate_commit": final_test["candidate_commit"],
        "post_test_tuning_performed": False,
        "live_telegram_used": False,
        "external_network_used": False,
        "synthetic_inputs_only": True,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "model": final_test["model"],
        },
        "cases": cases,
        "all_passed": all(bool(case["passed"]) for case in cases),
        "limitations": [
            "O cliente Telegram e o recurso HTTPS foram substituídos por objetos em memória.",
            "O ensaio não mede rede, Bot API, projeção, fala ou tempo total da apresentação.",
            "As saídas não foram avaliadas contra gabarito e não orientam ajustes pós-teste.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    if not report["all_passed"]:
        raise SystemExit("O ensaio local encontrou uma falha estrutural.")
    print(f"Ensaio aprovado e salvo em {output_path.relative_to(REPOSITORY)}")


def _run_case(
    name: str,
    handler: TelegramUpdateHandler,
    client: DemoClient,
    update: dict[str, Any],
) -> dict[str, object]:
    message_start = len(client.messages)
    event_start = len(client.events)
    started = time.perf_counter()
    outcome = handler.handle(update)
    elapsed_ms = (time.perf_counter() - started) * 1_000
    messages = [text for _, text in client.messages[message_start:]]
    events = client.events[event_start:]
    response = "".join(messages[1:]) if len(messages) >= 2 else ""
    checks = {
        "accepted_for_analysis": outcome.accepted_for_analysis,
        "processing_feedback_first": bool(messages) and messages[0] == PROCESSING_MESSAGE,
        "response_sections_present": all(section in response for section in REQUIRED_RESPONSE_SECTIONS),
        "response_within_telegram_chunk_limit": all(len(message) <= 4_096 for message in messages),
        "feedback_before_download_or_result": bool(events) and events[0] == "send",
    }
    return {
        "case": name,
        "passed": all(checks.values()),
        "elapsed_ms": elapsed_ms,
        "feedback_seconds": outcome.feedback_seconds,
        "message_count": len(messages),
        "checks": checks,
    }


def _run_rejection_case(
    handler: TelegramUpdateHandler,
    client: DemoClient,
    update: dict[str, Any],
) -> dict[str, object]:
    message_start = len(client.messages)
    started = time.perf_counter()
    outcome = handler.handle(update)
    elapsed_ms = (time.perf_counter() - started) * 1_000
    messages = [text for _, text in client.messages[message_start:]]
    checks = {
        "not_accepted_for_analysis": not outcome.accepted_for_analysis,
        "single_transparent_response": messages == [UNSUPPORTED_INPUT_MESSAGE],
    }
    return {
        "case": "unsupported_video",
        "passed": all(checks.values()),
        "elapsed_ms": elapsed_ms,
        "feedback_seconds": outcome.feedback_seconds,
        "message_count": len(messages),
        "checks": checks,
    }


def _demo_image() -> bytes:
    canvas = Image.new("RGB", (1_400, 500), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf"
    font = ImageFont.truetype(str(font_path), 54)
    draw.multiline_text(
        (70, 90),
        "ALEGACAO SOBRE VACINAS\n\nVacinas contem microchips para rastrear pessoas.",
        fill="black",
        font=font,
        spacing=22,
    )
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPOSITORY,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


if __name__ == "__main__":
    main()
