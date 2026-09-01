from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import OpenerDirector, Request, build_opener


class TelegramAPIError(RuntimeError):
    """Indica indisponibilidade ou resposta inválida da Telegram Bot API."""


class TelegramClient(Protocol):
    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict[str, Any], ...]: ...

    def send_message(self, chat_id: int, text: str) -> None: ...


@dataclass(slots=True)
class TelegramBotAPI:
    token: str
    request_timeout_seconds: float = 10.0
    max_response_bytes: int = 1_000_000
    _opener: OpenerDirector = field(default_factory=build_opener, repr=False)

    def __post_init__(self) -> None:
        self.token = self.token.strip()
        if not self.token or any(character.isspace() for character in self.token):
            raise ValueError("TELEGRAM_BOT_TOKEN está ausente ou é inválido.")
        if "/" in self.token or len(self.token) > 256:
            raise ValueError("TELEGRAM_BOT_TOKEN possui formato inválido.")
        if self.request_timeout_seconds <= 0 or self.max_response_bytes <= 0:
            raise ValueError("Timeout e limite de resposta devem ser positivos.")

    def get_updates(
        self,
        *,
        offset: int | None,
        timeout_seconds: int,
    ) -> tuple[dict[str, Any], ...]:
        if timeout_seconds <= 0 or timeout_seconds > 50:
            raise ValueError("O timeout do long polling deve estar entre 1 e 50 segundos.")
        payload: dict[str, str] = {
            "timeout": str(timeout_seconds),
            "allowed_updates": json.dumps(["message"]),
        }
        if offset is not None:
            payload["offset"] = str(offset)
        result = self._call(
            "getUpdates",
            payload,
            timeout_seconds=timeout_seconds + self.request_timeout_seconds,
        )
        if not isinstance(result, list) or any(not isinstance(item, dict) for item in result):
            raise TelegramAPIError("A Telegram Bot API retornou atualizações inválidas.")
        return tuple(result)

    def send_message(self, chat_id: int, text: str) -> None:
        if not text or len(text) > 4_096:
            raise ValueError("A mensagem ao Telegram deve conter de 1 a 4.096 caracteres.")
        self._call(
            "sendMessage",
            {
                "chat_id": str(chat_id),
                "text": text,
                "link_preview_options": json.dumps({"is_disabled": True}),
            },
            timeout_seconds=self.request_timeout_seconds,
        )

    def _call(
        self,
        method: str,
        payload: dict[str, str],
        *,
        timeout_seconds: float,
    ) -> Any:
        request = Request(
            f"https://api.telegram.org/bot{self.token}/{method}",
            data=urlencode(payload).encode("ascii"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                raw_response = response.read(self.max_response_bytes + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise TelegramAPIError("A Telegram Bot API não respondeu à solicitação.") from exc
        if len(raw_response) > self.max_response_bytes:
            raise TelegramAPIError("A resposta da Telegram Bot API excedeu o limite permitido.")
        try:
            envelope = json.loads(raw_response)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise TelegramAPIError("A Telegram Bot API retornou JSON inválido.") from exc
        if not isinstance(envelope, dict) or envelope.get("ok") is not True:
            raise TelegramAPIError("A Telegram Bot API recusou a solicitação.")
        if "result" not in envelope:
            raise TelegramAPIError("A Telegram Bot API retornou uma resposta incompleta.")
        return envelope["result"]
