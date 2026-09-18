"""Mede imagem, link e feedback local sem reutilizar o teste de qualidade."""

from __future__ import annotations

import argparse
import ctypes
import io
import json
import os
import platform
import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from immunocheck.application.content_normalizer import MultimodalNormalizer
from immunocheck.application.ports import ContentNormalizer
from immunocheck.application.text_components import TextNormalizer
from immunocheck.bootstrap import build_multimodal_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict
from immunocheck.evaluation.operational_performance import (
    summarize_latency,
    summarize_modality,
)
from immunocheck.infrastructure.ocr import TesseractOCR, inspect_image
from immunocheck.infrastructure.web_content import FetchedResource, SafeLinkTextExtractor
from immunocheck.telegram import TelegramUpdateHandler

REPOSITORY = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = REPOSITORY / "evaluation/results/performance/operational_records.jsonl"
DEFAULT_OUTPUT = REPOSITORY / "evaluation/results/performance/operational_performance.json"
FINAL_TEST = REPOSITORY / "evaluation/results/test/final_test.json"
CLAIMS = (
    "A vacina triplice viral causa autismo.",
    "Vacinas aprovadas passam por monitoramento de seguranca.",
    "A vacina contra covid altera o DNA humano.",
    "Vacinas infantis fortalecem a protecao contra doencas graves.",
    "A vacina contra influenza provoca a propria gripe.",
    "Eventos adversos graves depois de vacinas sao sempre ignorados.",
    "Duas doses podem ser necessarias para completar um esquema vacinal.",
    "Vacinas contem microchips para rastrear pessoas.",
    "A imunidade coletiva pode proteger pessoas vulneraveis.",
    "Toda reacao depois de uma vacina foi causada pela vacina.",
)
TARGETS_MS = {"image": 60_000.0, "link": 45_000.0, "telegram_feedback": 2_000.0}


@dataclass(slots=True)
class RecordingNormalizer:
    delegate: ContentNormalizer
    latency_ms: float | None = None

    def normalize(self, submission: ContentSubmission) -> str:
        started = time.perf_counter()
        try:
            return self.delegate.normalize(submission)
        finally:
            self.latency_ms = (time.perf_counter() - started) * 1_000


@dataclass(frozen=True, slots=True)
class MappingFetcher:
    resources: dict[str, FetchedResource]

    def fetch(self, url: str) -> FetchedResource:
        return self.resources[url]


@dataclass(slots=True)
class MemoryTelegramClient:
    sends: int = 0

    def send_message(self, chat_id: int, text: str) -> None:
        del chat_id, text
        self.sends += 1

    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict, ...]:
        del offset, timeout_seconds
        return ()

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes:
        del file_id, maximum_bytes
        raise AssertionError("O benchmark de feedback não deve baixar arquivos.")


@dataclass(frozen=True, slots=True)
class UnusedPipeline:
    def run(self, submission: ContentSubmission) -> FactCheckResult:
        del submission
        return FactCheckResult(
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            explanation="Pipeline não executada no benchmark de feedback.",
        )


@dataclass(slots=True)
class ResourceSampler:
    interval_seconds: float = 0.5
    samples: list[dict[str, float | None]] = field(default_factory=list)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)

    def start(self) -> None:
        self.samples.append(_resource_snapshot())
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, object]:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self.samples.append(_resource_snapshot())
        return _summarize_resources(self.samples)

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self.samples.append(_resource_snapshot())


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark operacional multimodal da v1.")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.runs < 30:
        parser.error("O protocolo exige ao menos 30 execuções por modalidade.")
    if args.output.exists():
        parser.error("O resultado operacional já existe; preserve a execução registrada.")

    final_test = json.loads(FINAL_TEST.read_text("utf-8"))
    pipeline = build_multimodal_pipeline(
        model=str(final_test["model"]),
        top_k=int(final_test["configuration"]["top_k"]),
        retrieval_mode="dense",
    )
    _warm_up(pipeline)
    existing = _load_records(args.records)
    sampler = ResourceSampler()
    sampler.start()
    try:
        _run_image_records(pipeline, existing, args.records, args.runs)
        _run_link_records(pipeline, existing, args.records, args.runs)
        _run_telegram_records(existing, args.records, args.runs)
    finally:
        resources = sampler.stop()

    records = _load_records(args.records)
    summaries = {
        modality: summarize_modality(
            [record for record in records if record["modality"] == modality],
            target_ms=TARGETS_MS[modality],
        )
        for modality in ("image", "link")
    }
    feedback = [record for record in records if record["modality"] == "telegram_feedback"]
    summaries["telegram_feedback"] = {
        "runs": len(feedback),
        "network_included": False,
        "feedback_latency": summarize_latency(
            [float(record["total_latency_ms"]) for record in feedback],
            target_ms=TARGETS_MS["telegram_feedback"],
        ),
    }
    result = {
        "schema_version": 1,
        "purpose": "operational_multimodal_performance_no_quality_tuning",
        "executed_at": datetime.now(UTC).isoformat(),
        "protocol": "docs/OPERATIONAL_PERFORMANCE_PROTOCOL.md",
        "current_commit": _git_head(),
        "final_quality_candidate_commit": final_test["candidate_commit"],
        "quality_test_reused": False,
        "post_test_tuning_performed": False,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "model": final_test["model"],
            "retrieval": "bge_m3_dense",
            "top_k": final_test["configuration"]["top_k"],
            "reranker": False,
            "auditor": final_test["configuration"]["faithfulness_auditor"],
        },
        "controlled_conditions": {
            "image": "synthetic_typographic_images_with_real_ocr",
            "link": "in_memory_https_resources_with_real_html_text_pdf_parsers",
            "telegram_feedback": "in_memory_client_without_bot_api_or_network",
        },
        "resources": resources,
        "summaries": summaries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(args.output)
    print(f"Resultado salvo em {args.output.relative_to(REPOSITORY)}", flush=True)


def _warm_up(pipeline: Any) -> None:
    pipeline.normalizer = TextNormalizer()
    started = time.perf_counter()
    pipeline.run(
        ContentSubmission(
            kind=ContentKind.TEXT,
            text="A vacina triplice viral causa autismo.",
        )
    )
    print(f"Aquecimento excluído: {time.perf_counter() - started:.2f}s", flush=True)


def _run_image_records(pipeline: Any, existing: list[dict[str, object]], path: Path, runs: int) -> None:
    normalizer = RecordingNormalizer(
        MultimodalNormalizer(TesseractOCR.from_environment(), SafeLinkTextExtractor())
    )
    pipeline.normalizer = normalizer
    for index in range(runs):
        record_id = f"image-{index + 1:03d}"
        if _contains(existing, record_id):
            continue
        image_format = ("PNG", "JPEG", "WEBP")[index % 3]
        submission = _image_submission(CLAIMS[index % len(CLAIMS)], image_format)
        record = _execute_pipeline(record_id, "image", image_format.lower(), pipeline, normalizer, submission)
        _append_record(path, record)
        existing.append(record)
        print(f"[{index + 1}/{runs}] imagem: {record['technical_error'] or record['verdict']}", flush=True)


def _run_link_records(pipeline: Any, existing: list[dict[str, object]], path: Path, runs: int) -> None:
    resources: dict[str, FetchedResource] = {}
    fixtures: list[tuple[str, str]] = []
    for index in range(runs):
        resource_type = ("html", "text", "pdf")[index % 3]
        url = f"https://benchmark.invalid/item-{index + 1:03d}.{resource_type}"
        claim = CLAIMS[index % len(CLAIMS)]
        resources[url] = _link_resource(url, resource_type, claim)
        fixtures.append((url, resource_type))
    normalizer = RecordingNormalizer(
        MultimodalNormalizer(
            TesseractOCR.from_environment(),
            SafeLinkTextExtractor(fetcher=MappingFetcher(resources)),  # type: ignore[arg-type]
        )
    )
    pipeline.normalizer = normalizer
    for index, (url, resource_type) in enumerate(fixtures):
        record_id = f"link-{index + 1:03d}"
        if _contains(existing, record_id):
            continue
        submission = ContentSubmission(kind=ContentKind.LINK, url=url)
        record = _execute_pipeline(record_id, "link", resource_type, pipeline, normalizer, submission)
        _append_record(path, record)
        existing.append(record)
        print(f"[{index + 1}/{runs}] link: {record['technical_error'] or record['verdict']}", flush=True)


def _run_telegram_records(existing: list[dict[str, object]], path: Path, runs: int) -> None:
    client = MemoryTelegramClient()
    handler = TelegramUpdateHandler(client=client, pipeline=UnusedPipeline())  # type: ignore[arg-type]
    for index in range(runs):
        record_id = f"telegram-feedback-{index + 1:03d}"
        if _contains(existing, record_id):
            continue
        update = {
            "update_id": index + 1,
            "message": {"chat": {"id": 10_000 + index}, "text": CLAIMS[index % len(CLAIMS)]},
        }
        started = time.perf_counter()
        pending = handler.prepare(update)
        elapsed_ms = (time.perf_counter() - started) * 1_000
        record = {
            "record_id": record_id,
            "modality": "telegram_feedback",
            "fixture_type": "in_memory_client",
            "total_latency_ms": elapsed_ms,
            "normalization_latency_ms": None,
            "technical_error": None if pending is not None else "feedback_not_prepared",
        }
        _append_record(path, record)
        existing.append(record)


def _execute_pipeline(
    record_id: str,
    modality: str,
    fixture_type: str,
    pipeline: Any,
    normalizer: RecordingNormalizer,
    submission: ContentSubmission,
) -> dict[str, object]:
    normalizer.latency_ms = None
    started = time.perf_counter()
    error = None
    verdict = None
    sources = 0
    try:
        result = pipeline.run(submission)
        verdict = result.verdict.value
        sources = len(result.sources)
    except Exception as exc:  # noqa: BLE001 - falhas entram no denominador do benchmark
        error = type(exc).__name__
    return {
        "record_id": record_id,
        "modality": modality,
        "fixture_type": fixture_type,
        "total_latency_ms": (time.perf_counter() - started) * 1_000,
        "normalization_latency_ms": normalizer.latency_ms,
        "technical_error": error,
        "verdict": verdict,
        "source_count": sources,
    }


def _image_submission(claim: str, image_format: str) -> ContentSubmission:
    canvas = Image.new("RGB", (1_400, 500), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf"
    font = ImageFont.truetype(str(font_path), 54)
    draw.multiline_text((70, 90), f"ALEGACAO SOBRE VACINAS\n\n{claim}", fill="black", font=font, spacing=22)
    buffer = io.BytesIO()
    save_options = {"quality": 88} if image_format == "JPEG" else {}
    canvas.save(buffer, format=image_format, **save_options)
    data = buffer.getvalue()
    media_type = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[image_format]
    info = inspect_image(data, declared_media_type=media_type)
    return ContentSubmission(
        kind=ContentKind.IMAGE,
        data=data,
        media_type=media_type,
        width=info.width,
        height=info.height,
    )


def _link_resource(url: str, resource_type: str, claim: str) -> FetchedResource:
    body_text = f"Boletim informativo sobre vacinacao. Alegacao analisada: {claim}"
    if resource_type == "html":
        body = f"<html><head><title>Boletim</title></head><body><main><p>{body_text}</p></main></body></html>".encode()
        return FetchedResource(url, "text/html; charset=utf-8", body)
    if resource_type == "text":
        return FetchedResource(url, "text/plain; charset=utf-8", body_text.encode())
    return FetchedResource(url, "application/pdf", _pdf_bytes(body_text))


def _pdf_bytes(text: str) -> bytes:
    safe_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    writer = PdfWriter()
    page = writer.add_blank_page(width=700, height=300)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 30 220 Td ({safe_text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(content)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _resource_snapshot() -> dict[str, float | None]:
    return {
        "timestamp": time.time(),
        "system_ram_used_gib": _windows_ram_used_gib(),
        "gpu_vram_used_gib": _nvidia_vram_used_gib(),
    }


def _windows_ram_used_gib() -> float | None:
    if os.name != "nt":
        return None

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return (status.total_physical - status.available_physical) / (1024**3)


def _nvidia_vram_used_gib() -> float | None:
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            check=True,
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        values = [float(line.strip()) for line in completed.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        return None
    return sum(values) / 1024 if values else None


def _summarize_resources(samples: list[dict[str, float | None]]) -> dict[str, object]:
    result: dict[str, object] = {"samples": len(samples), "scope": "whole_system"}
    for key, target in (("system_ram_used_gib", 24.0), ("gpu_vram_used_gib", 7.5)):
        values = [float(sample[key]) for sample in samples if sample[key] is not None]
        result[key] = (
            {
                "baseline_gib": values[0],
                "peak_gib": max(values),
                "peak_minus_baseline_gib": max(values) - values[0],
                "target_gib": target,
                "target_met_conservative_whole_system": max(values) <= target,
            }
            if values
            else {"available": False}
        )
    return result


def _contains(records: list[dict[str, object]], record_id: str) -> bool:
    return any(record.get("record_id") == record_id for record in records)


def _load_records(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def _append_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        output.flush()
        os.fsync(output.fileno())


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
