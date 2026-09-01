from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import OpenerDirector, Request, build_opener


class TelegramAPIError(RuntimeError):
    """Indica indisponibilidade ou resposta inválida da Telegram Bot API."""


class TelegramClient(Protocol):
    def get_updates(self, *, offset: int | None, timeout_seconds: int) -> tuple[dict[str, Any], ...]: ...

    def send_message(self, chat_id: int, text: str) -> None: ...

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes: ...


@dataclass(slots=True)
class TelegramBotAPI:
    token: str
    request_timeout_seconds: float = 10.0
    file_timeout_seconds: float = 10.0
    max_response_bytes: int = 1_000_000
    _opener: OpenerDirector = field(default_factory=build_opener, repr=False)

    def __post_init__(self) -> None:
        self.token = self.token.strip()
        if not self.token or any(character.isspace() for character in self.token):
            raise ValueError("TELEGRAM_BOT_TOKEN está ausente ou é inválido.")
        if "/" in self.token or len(self.token) > 256:
            raise ValueError("TELEGRAM_BOT_TOKEN possui formato inválido.")
        if (
            self.request_timeout_seconds <= 0
            or self.file_timeout_seconds <= 0
            or self.max_response_bytes <= 0
        ):
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

    def download_file(self, file_id: str, *, maximum_bytes: int) -> bytes:
        if not file_id or any(character.isspace() for character in file_id):
            raise TelegramAPIError("O identificador do arquivo do Telegram é inválido.")
        if maximum_bytes <= 0:
            raise ValueError("O limite do arquivo deve ser positivo.")
        result = self._call(
            "getFile",
            {"file_id": file_id},
            timeout_seconds=self.request_timeout_seconds,
        )
        if not isinstance(result, dict):
            raise TelegramAPIError("O Telegram retornou metadados de arquivo inválidos.")
        file_size = result.get("file_size")
        if file_size is not None and (not isinstance(file_size, int) or file_size < 0):
            raise TelegramAPIError("O Telegram retornou tamanho de arquivo inválido.")
        if isinstance(file_size, int) and file_size > maximum_bytes:
            raise TelegramAPIError("O arquivo excede o limite permitido.")
        file_path = result.get("file_path")
        if not isinstance(file_path, str) or not _is_safe_file_path(file_path):
            raise TelegramAPIError("O Telegram retornou caminho de arquivo inválido.")

        request = Request(
            f"https://api.telegram.org/file/bot{self.token}/{quote(file_path, safe='/')}",
            headers={"Accept-Encoding": "identity"},
            method="GET",
        )
        try:
            with self._opener.open(request, timeout=self.file_timeout_seconds) as response:
                declared_size = response.getheader("Content-Length")
                if declared_size is not None:
                    try:
                        numeric_size = int(declared_size)
                        if numeric_size < 0:
                            raise ValueError
                        if numeric_size > maximum_bytes:
                            raise TelegramAPIError("O arquivo excede o limite permitido.")
                    except ValueError as exc:
                        raise TelegramAPIError(
                            "O Telegram retornou tamanho de arquivo inválido."
                        ) from exc
                return _read_limited(response, maximum_bytes)
        except TelegramAPIError:
            raise
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise TelegramAPIError("Não foi possível baixar o arquivo do Telegram.") from exc

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


def _is_safe_file_path(file_path: str) -> bool:
    if not file_path or file_path.startswith(("/", "\\")) or "\\" in file_path:
        return False
    return all(part not in {"", ".", ".."} for part in file_path.split("/"))


def _read_limited(response: Any, maximum_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(64 * 1024, maximum_bytes - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > maximum_bytes:
            raise TelegramAPIError("O arquivo excede o limite permitido.")
        chunks.append(chunk)
    if not chunks:
        raise TelegramAPIError("O arquivo recebido está vazio.")
    return b"".join(chunks)
