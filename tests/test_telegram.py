from __future__ import annotations

import logging
from dataclasses import dataclass, field
from io import BytesIO

from PIL import Image

from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict
from immunocheck.telegram import (
    BUSY_MESSAGE,
    FEEDBACK_TARGET_SECONDS,
    PRIVACY_MESSAGE,
    PROCESSING_MESSAGE,
    START_MESSAGE,
    UNEXPECTED_ERROR_MESSAGE,
    UNSUPPORTED_INPUT_MESSAGE,
    TelegramUpdateHandler,
    _log_feedback_latency,
    _split_message,
)


@dataclass
class StubClient:
    messages: list[tuple[int, str]] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    file_content: bytes = b""
    downloads: list[tuple[str, int]] = field(default_factory=list)

    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict, ...]:
        del offset, timeout_seconds
        return ()

    def send_message(self, chat_id: int, text: str) -> None:
        self.events.append("send")
        self.messages.append((chat_id, text))

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes:
        self.downloads.append((file_id, maximum_bytes))
        return self.file_content


@dataclass
class StubPipeline:
    events: list[str]
    submissions: list[ContentSubmission] = field(default_factory=list)

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self.events.append("pipeline")
        self.submissions.append(submission)
        return FactCheckResult(
            verdict=Verdict.INSUFFICIENT_EVIDENCE,
            explanation="Não há informação suficiente.",
            claim=submission.text,
        )


class FailingPipeline:
    def run(self, submission: ContentSubmission) -> FactCheckResult:
        raise RuntimeError(f"falha ao processar conteúdo secreto: {submission.text}")


class Clock:
    def __init__(self, values: list[float]) -> None:
        self.values = iter(values)

    def __call__(self) -> float:
        return next(self.values)


def update_with_text(text: str) -> dict:
    return {"update_id": 1, "message": {"chat": {"id": 123}, "text": text}}


def png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (100, 50), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_sends_processing_feedback_before_running_pipeline() -> None:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(
        client=client,
        pipeline=pipeline,
        clock=Clock([10.0, 11.5, 13.0]),
    )

    outcome = handler.handle(update_with_text("Vacinas alteram o DNA?"))

    assert client.events[:2] == ["send", "pipeline"]
    assert client.messages[0] == (123, PROCESSING_MESSAGE)
    assert "🔍 NÃO DÁ PARA CONFIRMAR" in client.messages[1][1]
    assert outcome.accepted_for_analysis is True
    assert outcome.feedback_seconds == 1.5
    assert pipeline.submissions[0].text == "Vacinas alteram o DNA?"


def test_logs_feedback_latency_without_content_or_identifiers(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="immunocheck.telegram"):
        _log_feedback_latency(1.25)
        _log_feedback_latency(2.75)

    assert FEEDBACK_TARGET_SECONDS == 2.0
    assert "1.250 s" in caplog.text
    assert "2.750 s" in caplog.text
    assert "objetivo de até 2.0 s atendido" in caplog.text
    assert "objetivo de até 2.0 s excedido" in caplog.text
    assert "chat_id" not in caplog.text
    assert "file_id" not in caplog.text


def test_commands_are_handled_without_calling_pipeline() -> None:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(client=client, pipeline=pipeline)

    handler.handle(update_with_text("/start@ImmunoCheckBot"))
    handler.handle(update_with_text("/privacidade"))

    assert client.messages == [(123, START_MESSAGE), (123, PRIVACY_MESSAGE)]
    assert pipeline.submissions == []


def test_non_text_input_is_rejected_transparently() -> None:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(client=client, pipeline=pipeline)
    update = {"message": {"chat": {"id": 123}, "photo": [{"file_id": "abc"}]}}

    outcome = handler.handle(update)

    assert client.messages == [(123, UNSUPPORTED_INPUT_MESSAGE)]
    assert outcome.accepted_for_analysis is False
    assert pipeline.submissions == []


def test_standalone_https_url_is_routed_as_link() -> None:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(
        client=client,
        pipeline=pipeline,
        clock=Clock([10.0, 10.1, 11.0]),
    )

    handler.handle(update_with_text("https://example.org/noticia"))

    assert pipeline.submissions[0].kind is ContentKind.LINK
    assert pipeline.submissions[0].url == "https://example.org/noticia"


def test_image_is_downloaded_in_memory_and_routed_with_verified_metadata() -> None:
    client = StubClient(file_content=png_bytes())
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(
        client=client,
        pipeline=pipeline,
        clock=Clock([10.0, 10.1, 11.0]),
    )
    update = {
        "message": {
            "chat": {"id": 123},
            "document": {
                "file_id": "image-id",
                "file_size": len(client.file_content),
                "mime_type": "image/png",
            },
        }
    }

    handler.handle(update)

    submission = pipeline.submissions[0]
    assert client.downloads == [("image-id", 10 * 1024 * 1024)]
    assert submission.kind is ContentKind.IMAGE
    assert submission.data == client.file_content
    assert (submission.width, submission.height) == (100, 50)


def test_full_in_memory_queue_rejects_new_analysis_without_running_pipeline() -> None:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    handler = TelegramUpdateHandler(client=client, pipeline=pipeline)

    pending = handler.prepare(
        update_with_text("Uma alegação adicional"),
        accept_analysis=False,
    )

    assert pending is None
    assert client.messages == [(123, BUSY_MESSAGE)]
    assert pipeline.submissions == []


def test_unexpected_failure_does_not_expose_content_in_response_or_logs(caplog) -> None:
    client = StubClient()
    handler = TelegramUpdateHandler(
        client=client,
        pipeline=FailingPipeline(),
        clock=Clock([10.0, 10.1]),
    )

    with caplog.at_level(logging.ERROR):
        handler.handle(update_with_text("meu dado médico ultrassecreto"))

    assert client.messages[-1] == (123, UNEXPECTED_ERROR_MESSAGE)
    assert "ultrassecreto" not in caplog.text


def test_splits_long_messages_without_exceeding_telegram_limit() -> None:
    message = "a" * 4_000 + "\n" + "b" * 4_000 + "\n" + "c" * 1_000

    parts = _split_message(message)

    assert len(parts) == 3
    assert all(0 < len(part) <= 4_096 for part in parts)
    assert "".join(parts) == message.replace("\n", "")
