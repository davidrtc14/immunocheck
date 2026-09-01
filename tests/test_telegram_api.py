from __future__ import annotations

import json
from typing import Self
from urllib.parse import parse_qs

import pytest

from immunocheck.infrastructure.telegram_api import TelegramAPIError, TelegramBotAPI


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.headers: dict[str, str] = {}
        self.position = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, amount: int) -> bytes:
        chunk = self.raw[self.position : self.position + amount]
        self.position += len(chunk)
        return chunk

    def getheader(self, name: str) -> str | None:
        return self.headers.get(name)


class FakeOpener:
    def __init__(self, responses: list[object]) -> None:
        self.responses = responses
        self.requests: list[tuple[object, float]] = []

    def open(self, request: object, timeout: float) -> FakeResponse:
        self.requests.append((request, timeout))
        return FakeResponse(self.responses.pop(0))


def test_long_polling_uses_offset_timeout_and_only_message_updates() -> None:
    opener = FakeOpener(
        [{"ok": True, "result": [{"update_id": 10, "message": {"text": "teste"}}]}]
    )
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    updates = client.get_updates(offset=10, timeout_seconds=30)

    assert updates[0]["update_id"] == 10
    request, timeout = opener.requests[0]
    assert request.full_url.endswith("/getUpdates")
    payload = parse_qs(request.data.decode("ascii"))
    assert payload["offset"] == ["10"]
    assert payload["timeout"] == ["30"]
    assert json.loads(payload["allowed_updates"][0]) == ["message"]
    assert timeout == 40.0


def test_send_message_disables_link_preview() -> None:
    opener = FakeOpener([{"ok": True, "result": {"message_id": 1}}])
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    client.send_message(456, "Resposta com https://example.org")

    request, _ = opener.requests[0]
    payload = parse_qs(request.data.decode("ascii"))
    assert payload["chat_id"] == ["456"]
    assert json.loads(payload["link_preview_options"][0]) == {"is_disabled": True}


def test_api_error_does_not_expose_remote_description() -> None:
    opener = FakeOpener(
        [{"ok": False, "description": "conteúdo sensível que não deve ir para logs"}]
    )
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    with pytest.raises(TelegramAPIError) as captured:
        client.send_message(456, "teste")

    assert "conteúdo sensível" not in str(captured.value)


def test_download_file_validates_metadata_and_reads_only_to_limit() -> None:
    opener = FakeOpener(
        [
            {
                "ok": True,
                "result": {"file_size": 6, "file_path": "photos/teste.png"},
            },
            b"imagem",
        ]
    )
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    content = client.download_file("file-id", maximum_bytes=10)

    assert content == b"imagem"
    download_request, _ = opener.requests[1]
    assert download_request.full_url.endswith("/photos/teste.png")


@pytest.mark.parametrize("file_path", ["../token", "/absoluto", "pasta\\arquivo"])
def test_download_file_rejects_unsafe_remote_path(file_path: str) -> None:
    opener = FakeOpener(
        [{"ok": True, "result": {"file_size": 1, "file_path": file_path}}]
    )
    client = TelegramBotAPI(token="123:token-seguro", _opener=opener)  # type: ignore[arg-type]

    with pytest.raises(TelegramAPIError, match="caminho"):
        client.download_file("file-id", maximum_bytes=10)


@pytest.mark.parametrize("token", ["", "token com espaço", "token/com/barra"])
def test_rejects_invalid_token(token: str) -> None:
    with pytest.raises(ValueError):
        TelegramBotAPI(token=token)
