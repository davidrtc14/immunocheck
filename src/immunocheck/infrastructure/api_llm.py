"""Cliente de LLM por API compatível com OpenAI, só para o modo demonstração (ADR-057).

Implementa o mesmo `chat(...)` estruturado do cliente do Ollama, para que a pipeline v7 rode sem
mudança. As mensagens saem do computador: por isso o modo é opt-in, exige lista de permissão no bot e
não faz parte do sistema avaliado. Nada do conteúdo entra em logs; os erros usam mensagens fixas.
"""

from __future__ import annotations

import ipaddress
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import OpenerDirector, Request, build_opener

from immunocheck.infrastructure.ollama import OllamaError

RESPONSE_FORMATS = ("json_object", "json_schema")
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_THINK_BLOCK = re.compile(r"<think>.*?</think>", flags=re.DOTALL)
_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", flags=re.DOTALL)


class LLMAPIError(OllamaError):
    """Falha da API externa; herda de `OllamaError` para seguir o mesmo tratamento da pipeline."""


@dataclass(frozen=True, slots=True)
class OpenAICompatibleClient:
    api_key: str = field(repr=False)
    model: str
    base_url: str
    temperature: float = 0.0
    timeout_seconds: float = 60.0
    max_response_bytes: int = 1_000_000
    response_format: str = "json_schema"
    extra_body: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3
    _opener: OpenerDirector = field(default_factory=build_opener, repr=False)
    _sleep: Callable[[float], None] = field(default=time.sleep, repr=False)

    def __post_init__(self) -> None:
        if not self.api_key.strip() or any(c.isspace() for c in self.api_key.strip()):
            raise ValueError("LLM_API_KEY está ausente ou é inválida.")
        if not self.model.strip():
            raise ValueError("LLM_API_MODEL não pode ser vazio.")
        _validate_api_base_url(self.base_url)
        if self.response_format not in RESPONSE_FORMATS:
            raise ValueError(
                f"LLM_API_RESPONSE_FORMAT deve ser uma de: {', '.join(RESPONSE_FORMATS)}."
            )
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("A temperatura deve estar entre 0 e 2.")
        if self.timeout_seconds <= 0 or self.max_response_bytes <= 0 or self.max_retries < 0:
            raise ValueError("Timeout, limite de resposta e tentativas devem ser válidos.")

    def payload(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        # O schema vai no prompt, como no cliente do Ollama; o modo JSON da API garante a sintaxe.
        schema_instruction = (
            "\n\nResponda somente com um objeto JSON válido que obedeça exatamente a este schema, "
            "sem Markdown ou texto adicional:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        response_format: dict[str, Any] = {"type": "json_object"}
        if self.response_format == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": "resposta", "schema": schema},
            }
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt + schema_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": max_output_tokens,
            "response_format": response_format,
            **self.extra_body,
        }

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
        body = json.dumps(
            self.payload(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                max_output_tokens=max_output_tokens,
            ),
            ensure_ascii=False,
        ).encode("utf-8")
        return _parse_completion(self._post(body))

    def _post(self, body: bytes) -> bytes:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        for attempt in range(self.max_retries + 1):
            request = Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key.strip()}",
                },
                method="POST",
            )
            try:
                with self._opener.open(request, timeout=self.timeout_seconds) as response:
                    raw = response.read(self.max_response_bytes + 1)
            except HTTPError as exc:
                if exc.code in RETRYABLE_STATUS and attempt < self.max_retries:
                    self._sleep(_retry_delay(exc, attempt))
                    continue
                raise LLMAPIError(f"A API de LLM recusou a solicitação (HTTP {exc.code}).") from exc
            except (URLError, TimeoutError, OSError) as exc:
                if attempt < self.max_retries:
                    self._sleep(_retry_delay(None, attempt))
                    continue
                raise LLMAPIError("A API de LLM não respondeu à solicitação.") from exc
            if len(raw) > self.max_response_bytes:
                raise LLMAPIError("A resposta da API de LLM excedeu o limite permitido.")
            return raw
        raise LLMAPIError("A API de LLM não respondeu à solicitação.")


def _retry_delay(error: HTTPError | None, attempt: int) -> float:
    if error is not None:
        header = error.headers.get("Retry-After") if error.headers else None
        try:
            if header is not None:
                return min(max(float(header), 0.0), 60.0)
        except ValueError:
            pass
    return min(2.0 * (2**attempt), 30.0)


def _parse_completion(raw: bytes) -> dict[str, Any]:
    try:
        envelope = json.loads(raw)
        choice = envelope["choices"][0]
        if choice.get("finish_reason") == "length":
            raise LLMAPIError("A API de LLM interrompeu a resposta ao atingir o limite de tokens.")
        content = choice["message"]["content"]
        if not isinstance(content, str):
            raise TypeError
        text = _THINK_BLOCK.sub("", content).strip()
        fenced = _FENCE.match(text)
        if fenced:
            text = fenced.group(1)
        parsed = json.loads(text)
    except LLMAPIError:
        raise
    except (
        AttributeError,
        IndexError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as exc:
        raise LLMAPIError("A API de LLM retornou uma resposta estruturada inválida.") from exc
    if not isinstance(parsed, dict):
        raise LLMAPIError("O conteúdo estruturado da API de LLM não é um objeto JSON.")
    return parsed


def _validate_api_base_url(base_url: str) -> None:
    parsed = urlsplit(base_url)
    if parsed.scheme != "https":
        raise ValueError("LLM_API_BASE_URL deve usar HTTPS.")
    host = parsed.hostname or ""
    if not host or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("LLM_API_BASE_URL contém componentes não permitidos.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if host == "localhost" or host.endswith(".localhost"):
            raise ValueError("LLM_API_BASE_URL não pode apontar para o host local.") from None
        return
    if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
        raise ValueError("LLM_API_BASE_URL não pode apontar para endereço privado.")
