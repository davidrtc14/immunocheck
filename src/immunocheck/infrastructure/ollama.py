from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


class OllamaError(RuntimeError):
    """Indica indisponibilidade ou resposta inválida do Ollama local."""


@dataclass(frozen=True, slots=True)
class OllamaStructuredClient:
    model: str = "qwen3:8b"
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: float = 120.0
    max_response_bytes: int = 1_000_000
    context_tokens: int = 8_192

    def __post_init__(self) -> None:
        _validate_local_base_url(self.base_url)
        if not self.model.strip():
            raise ValueError("O nome do modelo Ollama não pode ser vazio.")
        if self.timeout_seconds <= 0 or self.max_response_bytes <= 0:
            raise ValueError("Timeout e limite de resposta devem ser positivos.")
        if self.context_tokens <= 0:
            raise ValueError("O contexto do modelo deve ser positivo.")

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        if max_output_tokens <= 0:
            raise ValueError("O limite de tokens de saída deve ser positivo.")
        schema_instruction = (
            "\n\nResponda somente com um objeto JSON válido que obedeça exatamente a este schema, "
            "sem Markdown ou texto adicional:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt + schema_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "seed": 42,
                "repeat_penalty": 1.1,
                "num_ctx": self.context_tokens,
                "num_predict": max_output_tokens,
            },
            "keep_alive": "10m",
        }
        request = Request(
            f"{self.base_url.rstrip('/')}/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # Ignorar proxies do sistema garante que o conteúdo permaneça no host local.
            with build_opener(ProxyHandler({})).open(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw_response = response.read(self.max_response_bytes + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise OllamaError("O Ollama local não respondeu à solicitação.") from exc

        if len(raw_response) > self.max_response_bytes:
            raise OllamaError("A resposta do Ollama excedeu o limite permitido.")
        return _parse_structured_response(raw_response)


def _validate_local_base_url(base_url: str) -> None:
    parsed = urlsplit(base_url)
    if parsed.scheme != "http":
        raise ValueError("A integração aceita apenas Ollama local por HTTP.")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("OLLAMA_BASE_URL deve apontar para o host local.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("OLLAMA_BASE_URL contém componentes não permitidos.")
    if parsed.path not in {"", "/"}:
        raise ValueError("OLLAMA_BASE_URL não deve conter um caminho.")
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("OLLAMA_BASE_URL contém uma porta inválida.") from exc


def _parse_structured_response(raw_response: bytes) -> dict[str, Any]:
    try:
        envelope = json.loads(raw_response)
        if envelope.get("done_reason") == "length":
            raise OllamaError("O Ollama interrompeu a resposta ao atingir o limite de tokens.")
        message = envelope["message"]
        content = message["content"]
        parsed_content = json.loads(content)
    except OllamaError:
        raise
    except (AttributeError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OllamaError("O Ollama retornou uma resposta estruturada inválida.") from exc
    if not isinstance(parsed_content, dict):
        raise OllamaError("O conteúdo estruturado do Ollama não é um objeto JSON.")
    return parsed_content
