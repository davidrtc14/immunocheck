"""Melhorias da demonstração: orientação nas abstenções, fila, "digitando…" e aquecimento."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from urllib.parse import parse_qs

from test_telegram_api import FakeOpener

from immunocheck.bootstrap_bot import WARMUP_CLAIM, warm_up_pipeline
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict
from immunocheck.infrastructure.telegram_api import TelegramAPIError, TelegramBotAPI
from immunocheck.presentation import INSUFFICIENT_GUIDANCE, NO_CLAIM_GUIDANCE, format_result
from immunocheck.telegram import PROCESSING_MESSAGE, TelegramUpdateHandler, _typing_indicator


def _text(result: FactCheckResult) -> str:
    return format_result(result, elapsed_seconds=1.0)


def test_insufficient_answer_explains_what_it_means_without_changing_verdict() -> None:
    output = _text(
        FactCheckResult.insufficient("As fontes não permitem concluir.", claim="Alegação.")
    )

    assert output.startswith("🔍 NÃO DÁ PARA CONFIRMAR")
    assert all(line in output for line in INSUFFICIENT_GUIDANCE)
    assert NO_CLAIM_GUIDANCE[0] not in output


def test_missing_claim_gets_instructions_instead_of_the_general_guidance() -> None:
    output = _text(FactCheckResult.insufficient("Não foi possível identificar uma alegação."))

    assert NO_CLAIM_GUIDANCE[0] in output
    assert INSUFFICIENT_GUIDANCE[0] not in output


def test_conclusive_answers_have_no_abstention_guidance() -> None:
    output = _text(FactCheckResult(verdict=Verdict.REFUTED, explanation="Contradiz.", claim="X."))

    assert INSUFFICIENT_GUIDANCE[0] not in output
    assert NO_CLAIM_GUIDANCE[0] not in output


@dataclass
class ActionClient:
    messages: list[str] = field(default_factory=list)
    actions: list[tuple[int, str]] = field(default_factory=list)
    fail_actions: bool = False

    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict, ...]:
        return ()

    def send_message(self, chat_id: int, text: str) -> None:
        self.messages.append(text)

    def send_chat_action(self, chat_id: int, action: str = "typing") -> None:
        self.actions.append((chat_id, action))
        if self.fail_actions:
            raise TelegramAPIError("falha simulada")

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes:
        return b""


class EchoPipeline:
    def run(self, submission: ContentSubmission) -> FactCheckResult:
        return FactCheckResult.insufficient("Sem evidência.", claim=submission.text)


def _update(text: str) -> dict:
    return {"update_id": 1, "message": {"chat": {"id": 7}, "text": text}}


def test_processing_message_reports_queue_position() -> None:
    client = ActionClient()
    handler = TelegramUpdateHandler(client=client, pipeline=EchoPipeline())

    handler.prepare(_update("A vacina X causa Y."))
    handler.prepare(_update("A vacina X causa Y."), queue_ahead=1)
    handler.prepare(_update("A vacina X causa Y."), queue_ahead=3)

    assert client.messages == [
        PROCESSING_MESSAGE,
        f"{PROCESSING_MESSAGE} Há 1 análise na sua frente.",
        f"{PROCESSING_MESSAGE} Há 3 análises na sua frente.",
    ]


def test_analysis_shows_typing_and_still_answers_when_the_indicator_fails() -> None:
    for fail in (False, True):
        client = ActionClient(fail_actions=fail)
        handler = TelegramUpdateHandler(client=client, pipeline=EchoPipeline())

        handler.handle(_update("A vacina X causa Y."))

        assert client.actions[0] == (7, "typing")
        assert client.messages[-1].startswith("🔍 NÃO DÁ PARA CONFIRMAR")


def test_typing_indicator_stops_its_thread_and_skips_clients_without_actions() -> None:
    client = ActionClient()
    with _typing_indicator(client, 7):
        pass
    assert not any(thread.name == "immunocheck-typing" for thread in threading.enumerate())

    class PlainClient:
        pass

    with _typing_indicator(PlainClient(), 7):  # type: ignore[arg-type]
        pass


def test_send_chat_action_calls_the_bot_api() -> None:
    opener = FakeOpener([{"ok": True, "result": True}])
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    client.send_chat_action(42)

    request, _ = opener.requests[0]
    assert request.full_url.endswith("/sendChatAction")  # type: ignore[attr-defined]
    assert parse_qs(request.data.decode()) == {"chat_id": ["42"], "action": ["typing"]}  # type: ignore[attr-defined]


def test_warm_up_runs_one_synthetic_text_claim() -> None:
    seen: list[ContentSubmission] = []

    class Recorder:
        def run(self, submission: ContentSubmission) -> FactCheckResult:
            seen.append(submission)
            return FactCheckResult.insufficient("ok", claim=submission.text)

    elapsed = warm_up_pipeline(Recorder())

    assert elapsed >= 0
    assert seen == [ContentSubmission(kind=ContentKind.TEXT, text=WARMUP_CLAIM)]


def test_repeated_sources_are_listed_once_without_changing_the_result() -> None:
    from immunocheck.domain.models import SourceReference

    def source(chunk_id: str, page: int) -> SourceReference:
        return SourceReference(
            chunk_id=chunk_id,
            source_name="Ministério da Saúde",
            document_title="HPV",
            url="https://www.gov.br/saude/hpv",
            page=page,
        )

    result = FactCheckResult(
        verdict=Verdict.SUPPORTED,
        explanation="Sustenta.",
        claim="X.",
        sources=(source("a", 1), source("b", 1), source("c", 2)),
    )

    output = _text(result)

    assert output.count("HPV — p. 1") == 1
    assert "  [2] Ministério da Saúde — HPV — p. 2" in output
    assert "[3]" not in output
    assert len(result.sources) == 3


def test_headline_uses_the_pipeline_correct_fact_once_and_falls_back_to_fixed_text() -> None:
    from immunocheck.presentation import NO_CLAIM_LABEL, VERDICT_SUMMARIES

    refuted = _text(
        FactCheckResult(
            verdict=Verdict.REFUTED,
            explanation="Contradiz.",
            claim="X causa Y.",
            correct_fact="X não causa Y.",
        )
    )
    assert refuted.splitlines()[:2] == ["❌ FALSO", "X não causa Y."]
    assert refuted.count("X não causa Y.") == 1

    supported = _text(FactCheckResult(verdict=Verdict.SUPPORTED, explanation="Ok.", claim="X."))
    assert supported.splitlines()[1] == VERDICT_SUMMARIES[Verdict.SUPPORTED]

    misleading = _text(
        FactCheckResult(
            verdict=Verdict.MISLEADING,
            explanation="Distorce.",
            claim="X.",
            omitted_or_distorted="Omite o qualificador.",
        )
    )
    assert misleading.splitlines()[1] == VERDICT_SUMMARIES[Verdict.MISLEADING]
    assert "🔎 O QUE FOI DISTORCIDO: Omite o qualificador." in misleading

    no_claim = _text(FactCheckResult.insufficient("Sem alegação."))
    assert no_claim.startswith(NO_CLAIM_LABEL)
