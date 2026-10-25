"""Modo demonstração (ADR-057): cliente de LLM por API e montagem no bot."""

from __future__ import annotations

import io
import json
from email.message import Message
from urllib.error import HTTPError

import pytest

from immunocheck import bootstrap, demo_mode, telegram
from immunocheck.infrastructure.api_llm import LLMAPIError, OpenAICompatibleClient
from immunocheck.infrastructure.context_budget import ContextBudgetClient
from immunocheck.infrastructure.ollama import OllamaError

SCHEMA = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return _Response(json.dumps(outcome).encode())


def _completion(content: str, finish_reason: str = "stop") -> dict:
    return {"choices": [{"finish_reason": finish_reason, "message": {"content": content}}]}


def _http_error(code: int, retry_after: str | None = None, body: bytes = b"") -> HTTPError:
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return HTTPError("https://api.example.com", code, "erro", headers, io.BytesIO(body))


def _client(opener, **kwargs) -> OpenAICompatibleClient:
    sleeps: list[float] = []
    client = OpenAICompatibleClient(
        api_key="chave-de-teste",
        model="modelo-teste",
        base_url="https://api.example.com/openai/v1",
        _opener=opener,
        _sleep=sleeps.append,
        **kwargs,
    )
    return client


def _chat(client):
    return client.chat(
        system_prompt="Sistema.", user_prompt="Usuário.", schema=SCHEMA, max_output_tokens=50
    )


def test_sends_openai_compatible_request_and_parses_json() -> None:
    opener = FakeOpener([_completion('{"ok": true}')])

    client = _client(opener, response_format="json_object", extra_body={"reasoning_effort": "none"})
    assert _chat(client) == {"ok": True}

    request = opener.requests[0]
    body = json.loads(request.data)
    assert request.full_url == "https://api.example.com/openai/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer chave-de-teste"
    assert request.get_header("User-agent").startswith("ImmunoCheck-TCC/")
    assert body["model"] == "modelo-teste"
    assert body["response_format"] == {"type": "json_object"}
    assert body["max_tokens"] == 50
    assert body["reasoning_effort"] == "none"
    assert '"required": ["ok"]' in body["messages"][0]["content"]


def test_json_schema_is_the_default_and_sends_the_schema() -> None:
    opener = FakeOpener([_completion('{"ok": false}')])

    _chat(_client(opener))

    sent = json.loads(opener.requests[0].data)["response_format"]
    assert sent == {"type": "json_schema", "json_schema": {"name": "resposta", "schema": SCHEMA}}


def test_strips_reasoning_and_markdown_fences() -> None:
    content = '<think>pensando</think>\n```json\n{"ok": true}\n```'
    assert _chat(_client(FakeOpener([_completion(content)]))) == {"ok": True}


@pytest.mark.parametrize(
    "outcome",
    [
        _completion('{"ok": true}', finish_reason="length"),
        _completion("não é json"),
        {"choices": []},
    ],
)
def test_invalid_answers_raise_the_pipeline_error(outcome) -> None:
    with pytest.raises(LLMAPIError) as error:
        _chat(_client(FakeOpener([outcome])))
    assert isinstance(error.value, OllamaError)


def test_retries_rate_limits_and_then_gives_up() -> None:
    opener = FakeOpener([_http_error(429, "1"), _completion('{"ok": true}')])
    assert _chat(_client(opener)) == {"ok": True}
    assert len(opener.requests) == 2

    failing = FakeOpener([_http_error(429)] * 4)
    with pytest.raises(LLMAPIError, match="HTTP 429"):
        _chat(_client(failing))
    assert len(failing.requests) == 4

    unauthorized = FakeOpener([_http_error(401)])
    with pytest.raises(LLMAPIError, match="HTTP 401"):
        _chat(_client(unauthorized))
    assert len(unauthorized.requests) == 1


@pytest.mark.parametrize(
    "url",
    [
        "http://api.example.com/v1",
        "https://localhost/v1",
        "https://127.0.0.1/v1",
        "https://10.0.0.5/v1",
    ],
)
def test_rejects_insecure_or_local_endpoints(url) -> None:
    with pytest.raises(ValueError, match="LLM_API_BASE_URL"):
        OpenAICompatibleClient(api_key="k", model="m", base_url=url)


def test_api_key_is_not_in_repr() -> None:
    assert "chave-de-teste" not in repr(_client(FakeOpener([])))


def test_backend_selection_and_configuration_errors() -> None:
    assert demo_mode.resolve_backend({}) == "ollama"
    assert demo_mode.is_demo_mode({"LLM_BACKEND": "API"})
    with pytest.raises(ValueError, match="LLM_BACKEND"):
        demo_mode.resolve_backend({"LLM_BACKEND": "outro"})
    with pytest.raises(ValueError, match="LLM_API_KEY"):
        demo_mode.build_api_client({"LLM_API_MODEL": "m"})
    with pytest.raises(ValueError, match="LLM_API_EXTRA_JSON"):
        demo_mode.build_api_client(
            {"LLM_API_KEY": "k", "LLM_API_MODEL": "m", "LLM_API_EXTRA_JSON": "[1]"}
        )

    client = demo_mode.build_api_client({"LLM_API_KEY": "k", "LLM_API_MODEL": "m"})
    assert isinstance(client, ContextBudgetClient)
    assert client.delegate.base_url == demo_mode.DEFAULT_API_BASE_URL


def test_install_replaces_the_llm_client_builder(monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "_build_llm_client", bootstrap._build_llm_client)
    demo_mode.install_api_backend({"LLM_API_KEY": "k", "LLM_API_MODEL": "m"})

    client = bootstrap._build_llm_client(model=None, base_url=None, temperature=0.3)

    assert isinstance(client.delegate, OpenAICompatibleClient)
    assert client.delegate.model == "m"
    assert client.delegate.temperature == 0.3


def test_demo_messages_warn_about_the_external_api() -> None:
    assert demo_mode.DEMO_NOTICE in telegram.DEMO_START_MESSAGE
    assert "localmente" not in telegram.DEMO_PRIVACY_MESSAGE
    assert "local" not in telegram.DEMO_PROCESSING_MESSAGE


def test_demo_bot_refuses_to_start_without_an_allowlist(monkeypatch, capsys) -> None:
    monkeypatch.setenv("LLM_BACKEND", "api")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:token-de-teste")
    monkeypatch.delenv("TELEGRAM_ALLOWED_CHAT_IDS", raising=False)
    monkeypatch.delenv("DEMO_ALLOW_PUBLIC", raising=False)
    monkeypatch.setattr(demo_mode, "install_api_backend", lambda: None)
    monkeypatch.setattr(telegram, "build_bot_multimodal_pipeline", lambda: object())

    assert telegram.main() == 2
    assert "TELEGRAM_ALLOWED_CHAT_IDS" in capsys.readouterr().err


def test_retries_when_the_provider_rejects_the_generated_json() -> None:
    rejected = _http_error(400, body=b'{"error": {"code": "json_validate_failed"}}')
    opener = FakeOpener([rejected, _completion('{"ok": true}')])

    assert _chat(_client(opener)) == {"ok": True}
    assert len(opener.requests) == 2
