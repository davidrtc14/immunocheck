"""Cliente Ollama com semente configurável (candidata C5 da v7, ADR-054).

`ollama.py` está congelado pela Fase 18 e fixa a semente em 42. O voto por consistência precisa de
amostras diferentes, então este cliente repete a mesma chamada com a semente como parâmetro e reusa a
validação de endereço local e o parser estruturado do módulo congelado.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from immunocheck.infrastructure.ollama import (
    OllamaError,
    _parse_structured_response,
    _validate_local_base_url,
)


@dataclass(frozen=True, slots=True)
class SeededOllamaClient:
    model: str = "qwen3:8b"
    base_url: str = "http://127.0.0.1:11434"
    seed: int = 42
    temperature: float = 0.0
    timeout_seconds: float = 120.0
    max_response_bytes: int = 1_000_000
    context_tokens: int = 8_192

    def __post_init__(self) -> None:
        _validate_local_base_url(self.base_url)
        if not self.model.strip():
            raise ValueError("O nome do modelo Ollama não pode ser vazio.")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("A temperatura deve estar entre 0 e 2.")

    def payload(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        schema_instruction = (
            "\n\nResponda somente com um objeto JSON válido que obedeça exatamente a este schema, "
            "sem Markdown ou texto adicional:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt + schema_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "format": schema,
            "options": {
                "temperature": self.temperature,
                "seed": self.seed,
                "repeat_penalty": 1.1,
                "num_ctx": self.context_tokens,
                "num_predict": max_output_tokens,
            },
            "keep_alive": "10m",
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
        body = self.payload(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema,
            max_output_tokens=max_output_tokens,
        )
        request = Request(
            f"{self.base_url.rstrip('/')}/api/chat",
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # Ignorar proxies do sistema garante que o conteúdo permaneça no host local.
            with build_opener(ProxyHandler({})).open(
                request, timeout=self.timeout_seconds
            ) as response:
                raw_response = response.read(self.max_response_bytes + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise OllamaError("O Ollama local não respondeu à solicitação.") from exc
        if len(raw_response) > self.max_response_bytes:
            raise OllamaError("A resposta do Ollama excedeu o limite permitido.")
        return _parse_structured_response(raw_response)
