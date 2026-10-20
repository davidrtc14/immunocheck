from __future__ import annotations

import logging
import os
import sys
import threading
import time
from collections.abc import Callable, Iterator
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol

from immunocheck.application.content_normalizer import ContentExtractionError
from immunocheck.application.input_understanding import route_message
from immunocheck.application.text_components import ModelOutputError
from immunocheck.bootstrap import resolve_extraction_version
from immunocheck.bootstrap_bot import build_bot_multimodal_pipeline, warm_up_pipeline
from immunocheck.bot_access import AccessPolicy
from immunocheck.domain.input_policy import InputLimits, InvalidSubmissionError
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult
from immunocheck.infrastructure.ocr import inspect_image
from immunocheck.infrastructure.ollama import OllamaError
from immunocheck.infrastructure.telegram_api import (
    TelegramAPIError,
    TelegramBotAPI,
    TelegramClient,
)
from immunocheck.presentation import format_result
from immunocheck.retrieval.pilot_corpus import CorpusLoadError

LOGGER = logging.getLogger("immunocheck.telegram")
FEEDBACK_TARGET_SECONDS = 2.0
PROCESSING_MESSAGE = (
    "Recebi o conteúdo. A análise local foi iniciada e costuma levar de 15 a 40 segundos."
)
TYPING_REFRESH_SECONDS = 4.0
UNAVAILABLE_MESSAGE = (
    "Não foi possível concluir a análise agora porque um componente local está indisponível. "
    "Tente novamente em alguns minutos."
)
UNEXPECTED_ERROR_MESSAGE = "Não foi possível concluir a análise devido a uma falha interna. Nenhum conteúdo foi armazenado."
UNSUPPORTED_INPUT_MESSAGE = (
    "Envie uma alegação em texto, uma imagem textual em PNG/JPEG/WebP ou uma URL HTTPS. "
    "Vídeo, áudio e outros arquivos não são aceitos na v1."
)
BUSY_MESSAGE = (
    "O protótipo já possui várias análises na fila. Aguarde a conclusão e tente novamente."
)
RATE_LIMIT_MESSAGE = (
    "Você enviou mensagens demais em pouco tempo. Aguarde um minuto e tente novamente."
)
START_MESSAGE = """ImmunoCheck — verificação acadêmica de alegações sobre vacinação humana.

Envie uma alegação em texto, imagem predominantemente textual ou URL HTTPS pública. O sistema compara o conteúdo com fontes documentais e apresenta um veredito rastreável. Ele não oferece orientação médica individual.

O ImmunoCheck não mantém memória entre mensagens nem grava localmente o conteúdo ou seu identificador. A mensagem transita pelo Telegram e está sujeita às políticas da plataforma.

Comandos: /ajuda e /privacidade."""
HELP_MESSAGE = """Como usar:
1. Envie uma alegação factual sobre vacinação humana em texto, imagem textual ou link HTTPS.
2. Aguarde a análise local.
3. Confira o veredito, a explicação e as fontes apresentadas.

Uma mensagem deve conter uma alegação principal. Não envie dados médicos pessoais."""
PRIVACY_MESSAGE = """Privacidade:
- o ImmunoCheck processa a mensagem localmente e não a grava;
- não há histórico ou memória conversacional;
- conteúdo e identificadores não entram nos logs;
- o Telegram processa e pode conservar mensagens conforme suas próprias políticas;
- não envie dados médicos pessoais desnecessários."""


class FactCheckRunner(Protocol):
    def run(self, submission: ContentSubmission) -> FactCheckResult: ...


@dataclass(frozen=True, slots=True)
class HandlingResult:
    accepted_for_analysis: bool
    feedback_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class PendingAnalysis:
    chat_id: int
    submission: ContentSubmission
    started_at: float
    feedback_seconds: float
    telegram_file_id: str | None = None


@dataclass(slots=True)
class TelegramUpdateHandler:
    client: TelegramClient
    pipeline: FactCheckRunner
    clock: Callable[[], float] = time.perf_counter
    input_limits: InputLimits | None = None
    access: AccessPolicy | None = None
    # v1: só uma URL isolada vira link; v2 (ADR-050): URL com comentário também.
    message_router: Callable[[str], ContentSubmission] = field(
        default_factory=lambda: legacy_route_message
    )

    def __post_init__(self) -> None:
        # Fonte única dos limites: a pipeline que valida a entrada, salvo configuração explícita.
        if self.input_limits is None:
            self.input_limits = getattr(self.pipeline, "input_limits", None) or InputLimits()

    def handle(self, update: dict[str, Any]) -> HandlingResult:
        pending = self.prepare(update)
        if pending is None:
            return HandlingResult(accepted_for_analysis=False)
        self.process(pending)
        return HandlingResult(
            accepted_for_analysis=True,
            feedback_seconds=pending.feedback_seconds,
        )

    def prepare(
        self,
        update: dict[str, Any],
        *,
        accept_analysis: bool = True,
        queue_ahead: int = 0,
    ) -> PendingAnalysis | None:
        message = update.get("message")
        if not isinstance(message, dict):
            return None
        chat = message.get("chat")
        if not isinstance(chat, dict) or not isinstance(chat.get("id"), int):
            return None
        chat_id = chat["id"]
        if self.access is not None:
            if not self.access.is_allowed(chat_id):
                return None
            if not self.access.limiter.allow(chat_id):
                if self.access.limiter.should_notify(chat_id):
                    self.client.send_message(chat_id, RATE_LIMIT_MESSAGE)
                return None
        submission: ContentSubmission
        telegram_file_id: str | None = None
        text = message.get("text")
        if isinstance(text, str):
            normalized_text = text.strip()
            if not normalized_text:
                return None
            command = _command_name(normalized_text)
            if command == "/start":
                self.client.send_message(chat_id, START_MESSAGE)
                return None
            if command in {"/help", "/ajuda"}:
                self.client.send_message(chat_id, HELP_MESSAGE)
                return None
            if command == "/privacidade":
                self.client.send_message(chat_id, PRIVACY_MESSAGE)
                return None
            if command is not None:
                self.client.send_message(chat_id, "Comando não reconhecido. Use /ajuda.")
                return None
            submission = self.message_router(normalized_text)
        else:
            try:
                image_descriptor = _telegram_image_descriptor(message, self.input_limits)
            except InvalidSubmissionError as exc:
                self.client.send_message(chat_id, f"Não foi possível analisar o conteúdo: {exc}")
                return None
            if image_descriptor is None:
                self.client.send_message(chat_id, UNSUPPORTED_INPUT_MESSAGE)
                return None
            submission, telegram_file_id = image_descriptor
        if not accept_analysis:
            self.client.send_message(chat_id, BUSY_MESSAGE)
            return None

        started_at = self.clock()
        self.client.send_message(chat_id, _processing_message(queue_ahead))
        feedback_seconds = self.clock() - started_at
        return PendingAnalysis(
            chat_id=chat_id,
            submission=submission,
            started_at=started_at,
            feedback_seconds=feedback_seconds,
            telegram_file_id=telegram_file_id,
        )

    def process(self, pending: PendingAnalysis) -> None:
        with _typing_indicator(self.client, pending.chat_id):
            response = self._analyze(pending)
        _send_text(self.client, pending.chat_id, response)

    def _analyze(self, pending: PendingAnalysis) -> str:
        try:
            submission = pending.submission
            if pending.telegram_file_id is not None:
                data = self.client.download_file(
                    pending.telegram_file_id,
                    maximum_bytes=self.input_limits.max_image_bytes,
                )
                info = inspect_image(
                    data,
                    declared_media_type=submission.media_type,
                    maximum_pixels=self.input_limits.max_image_pixels,
                )
                if (
                    submission.width is not None
                    and submission.height is not None
                    and (submission.width, submission.height) != (info.width, info.height)
                ):
                    raise ContentExtractionError(
                        "As dimensões informadas pelo Telegram são inconsistentes."
                    )
                submission = ContentSubmission(
                    kind=ContentKind.IMAGE,
                    text=submission.text,
                    data=data,
                    media_type=info.media_type,
                    width=info.width,
                    height=info.height,
                )
            result = self.pipeline.run(submission)
            response = format_result(result, elapsed_seconds=self.clock() - pending.started_at)
        except (InvalidSubmissionError, ContentExtractionError) as exc:
            response = f"Não foi possível analisar o conteúdo: {exc}"
        except TelegramAPIError:
            response = "Não foi possível baixar a imagem do Telegram. Tente enviá-la novamente."
        except (CorpusLoadError, OllamaError, ModelOutputError):
            response = UNAVAILABLE_MESSAGE
            LOGGER.error("Análise indisponível; categoria de falha conhecida.")
        # A fronteira pública precisa responder de modo seguro até para falhas imprevistas.
        except Exception:  # noqa: BLE001
            response = UNEXPECTED_ERROR_MESSAGE
            LOGGER.error("Falha interna inesperada durante a análise.")
        return response


@dataclass(slots=True)
class TelegramLongPoller:
    client: TelegramClient
    handler: TelegramUpdateHandler
    polling_timeout_seconds: int = 30
    maximum_backoff_seconds: float = 30.0
    maximum_pending_analyses: int = 4
    sleep: Callable[[float], None] = time.sleep
    _offset: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not 1 <= self.polling_timeout_seconds <= 50:
            raise ValueError("O timeout do long polling deve estar entre 1 e 50 segundos.")
        if self.maximum_backoff_seconds <= 0 or self.maximum_pending_analyses <= 0:
            raise ValueError("Backoff e limite da fila devem ser positivos.")

    def run_forever(self) -> None:
        backoff_seconds = 1.0
        pending_futures: set[Future[None]] = set()
        executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="immunocheck-analysis")
        try:
            while True:
                try:
                    updates = self.client.get_updates(
                        offset=self._offset,
                        timeout_seconds=self.polling_timeout_seconds,
                    )
                    backoff_seconds = 1.0
                except TelegramAPIError:
                    LOGGER.warning(
                        "Telegram temporariamente indisponível; nova tentativa agendada."
                    )
                    self.sleep(backoff_seconds)
                    backoff_seconds = min(backoff_seconds * 2, self.maximum_backoff_seconds)
                    continue

                pending_futures = {future for future in pending_futures if not future.done()}
                for update in updates:
                    update_id = update.get("update_id")
                    if isinstance(update_id, int):
                        self._offset = update_id + 1
                    capacity_available = len(pending_futures) < self.maximum_pending_analyses
                    try:
                        pending = self.handler.prepare(
                            update,
                            accept_analysis=capacity_available,
                            queue_ahead=len(pending_futures),
                        )
                    except TelegramAPIError:
                        LOGGER.warning("Não foi possível enviar uma resposta ao Telegram.")
                        continue
                    if pending is None:
                        continue
                    _log_feedback_latency(pending.feedback_seconds)
                    future = executor.submit(self._process_safely, pending)
                    pending_futures.add(future)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _process_safely(self, pending: PendingAnalysis) -> None:
        try:
            self.handler.process(pending)
        except TelegramAPIError:
            LOGGER.warning("Não foi possível enviar uma resposta ao Telegram.")


def main() -> int:
    _configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    try:
        client = TelegramBotAPI(token=token, request_timeout_seconds=2.0)
        pipeline = build_bot_multimodal_pipeline()
        access = AccessPolicy.from_environment(os.environ)
        router = route_message if resolve_extraction_version() == "v2" else legacy_route_message
    except (ValueError, CorpusLoadError) as exc:
        print(f"Configuração inválida: {exc}", file=sys.stderr)
        return 2

    if os.getenv("BOT_WARMUP", "1").strip() != "0":
        LOGGER.info("Aquecendo os modelos locais com uma alegação sintética.")
        try:
            LOGGER.info("Modelos aquecidos em %.1f s.", warm_up_pipeline(pipeline))
        except Exception:  # noqa: BLE001 - o aquecimento é opcional e não impede o bot
            LOGGER.warning("Aquecimento falhou; a primeira análise carregará os modelos.")
    LOGGER.info("Bot iniciado por long polling, sem persistência de interações.")
    poller = TelegramLongPoller(
        client=client,
        handler=TelegramUpdateHandler(
            client=client, pipeline=pipeline, access=access, message_router=router
        ),
    )
    try:
        poller.run_forever()
    except KeyboardInterrupt:
        LOGGER.info("Bot encerrado pelo operador.")
    return 0


def _processing_message(queue_ahead: int) -> str:
    if queue_ahead <= 0:
        return PROCESSING_MESSAGE
    plural = "análise" if queue_ahead == 1 else "análises"
    return f"{PROCESSING_MESSAGE} Há {queue_ahead} {plural} na sua frente."


@contextmanager
def _typing_indicator(client: TelegramClient, chat_id: int) -> Iterator[None]:
    """Renova "digitando…" enquanto a análise roda; falhas do indicador não afetam a resposta."""

    send = getattr(client, "send_chat_action", None)
    if send is None:
        yield
        return
    stop = threading.Event()

    def refresh() -> None:
        while True:
            try:
                send(chat_id, "typing")
            except TelegramAPIError:
                return
            if stop.wait(TYPING_REFRESH_SECONDS):
                return

    thread = threading.Thread(target=refresh, name="immunocheck-typing", daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1.0)


def _command_name(text: str) -> str | None:
    first_token = text.split(maxsplit=1)[0]
    if not first_token.startswith("/"):
        return None
    return first_token.split("@", maxsplit=1)[0].lower()


def _log_feedback_latency(feedback_seconds: float) -> None:
    if feedback_seconds > FEEDBACK_TARGET_SECONDS:
        LOGGER.warning(
            "Feedback de processamento enviado em %.3f s; objetivo de até %.1f s excedido.",
            feedback_seconds,
            FEEDBACK_TARGET_SECONDS,
        )
        return
    LOGGER.info(
        "Feedback de processamento enviado em %.3f s; objetivo de até %.1f s atendido.",
        feedback_seconds,
        FEEDBACK_TARGET_SECONDS,
    )


def legacy_route_message(text: str) -> ContentSubmission:
    if _looks_like_standalone_url(text):
        return ContentSubmission(kind=ContentKind.LINK, url=text)
    return ContentSubmission(kind=ContentKind.TEXT, text=text)


def _looks_like_standalone_url(text: str) -> bool:
    return " " not in text and text.lower().startswith(("http://", "https://"))


def _caption(message: dict[str, Any]) -> str | None:
    caption = message.get("caption")
    return caption.strip() or None if isinstance(caption, str) else None


def _telegram_image_descriptor(
    message: dict[str, Any],
    limits: InputLimits,
) -> tuple[ContentSubmission, str] | None:
    photos = message.get("photo")
    if isinstance(photos, list) and photos:
        photo = photos[-1]
        if not isinstance(photo, dict):
            return None
        file_id = photo.get("file_id")
        width = photo.get("width")
        height = photo.get("height")
        file_size = photo.get("file_size")
        if (
            not isinstance(file_id, str)
            or not isinstance(width, int)
            or not isinstance(height, int)
        ):
            return None
        _validate_telegram_image_metadata(width, height, file_size, limits)
        return (
            ContentSubmission(
                kind=ContentKind.IMAGE,
                text=_caption(message),
                media_type="image/jpeg",
                width=width,
                height=height,
            ),
            file_id,
        )

    document = message.get("document")
    if not isinstance(document, dict):
        return None
    media_type = document.get("mime_type")
    file_id = document.get("file_id")
    file_size = document.get("file_size")
    if media_type not in limits.allowed_image_types or not isinstance(file_id, str):
        return None
    _validate_telegram_image_metadata(None, None, file_size, limits)
    return (
        ContentSubmission(kind=ContentKind.IMAGE, text=_caption(message), media_type=media_type),
        file_id,
    )


def _validate_telegram_image_metadata(
    width: int | None,
    height: int | None,
    file_size: object,
    limits: InputLimits,
) -> None:
    if file_size is not None and (not isinstance(file_size, int) or file_size < 0):
        raise InvalidSubmissionError("O Telegram informou tamanho de imagem inválido.")
    if isinstance(file_size, int) and file_size > limits.max_image_bytes:
        raise InvalidSubmissionError("A imagem excede o limite de 10 MB.")
    if width is not None and height is not None:
        if width <= 0 or height <= 0:
            raise InvalidSubmissionError("As dimensões da imagem são inválidas.")
        if width * height > limits.max_image_pixels:
            raise InvalidSubmissionError("A imagem excede o limite de 12 megapixels.")


def _send_text(client: TelegramClient, chat_id: int, text: str) -> None:
    for part in _split_message(text):
        client.send_message(chat_id, part)


def _split_message(text: str, max_chars: int = 4_096) -> tuple[str, ...]:
    if max_chars <= 0:
        raise ValueError("O limite de mensagem deve ser positivo.")
    if len(text) <= max_chars:
        return (text,)
    parts: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            parts.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, max_chars + 1)
        if split_at <= 0:
            split_at = max_chars
        part = remaining[:split_at].rstrip()
        if not part:
            part = remaining[:max_chars]
            split_at = max_chars
        parts.append(part)
        remaining = remaining[split_at:].lstrip("\n")
    return tuple(parts)


def _configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


if __name__ == "__main__":
    raise SystemExit(main())
