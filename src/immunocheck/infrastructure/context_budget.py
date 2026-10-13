from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from immunocheck.infrastructure.ollama import OllamaError

# Chaves que carregam texto longo e não confiável nos prompts da pipeline.
TRUNCATABLE_KEYS = frozenset({"text", "content", "texto_do_usuario"})
TRUNCATION_MARK = " […]"


class ContextBudgetError(OllamaError):
    """A entrada não cabe no contexto do modelo mesmo após truncar a evidência."""


class ChatClient(Protocol):
    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class ContextBudgetClient:
    """Estima tokens antes de chamar o LLM e trunca cada trecho, nunca o prompt de sistema.

    Sem tokenizador local, usa-se uma razão conservadora de caracteres por token para
    texto em português dentro de JSON. Prompts que já cabem passam inalterados.
    """

    delegate: ChatClient
    context_tokens: int = 8_192
    chars_per_token: float = 2.8
    reserve_tokens: int = 256
    min_chunk_chars: int = 300

    def __post_init__(self) -> None:
        if self.context_tokens <= 0 or self.chars_per_token <= 0:
            raise ValueError("Contexto e razão de caracteres por token devem ser positivos.")
        if self.reserve_tokens < 0 or self.min_chunk_chars <= 0:
            raise ValueError("Reserva e tamanho mínimo de trecho são inválidos.")

    def chat(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        max_output_tokens: int,
    ) -> dict[str, Any]:
        fixed_chars = len(system_prompt) + len(json.dumps(schema, ensure_ascii=False))
        budget_chars = int(
            (self.context_tokens - max_output_tokens - self.reserve_tokens)
            * self.chars_per_token
        ) - fixed_chars
        if budget_chars <= 0:
            raise ContextBudgetError("O prompt fixo excede o contexto do modelo.")
        return self.delegate.chat(
            system_prompt=system_prompt,
            user_prompt=self._fit(user_prompt, budget_chars),
            schema=schema,
            max_output_tokens=max_output_tokens,
        )

    def _fit(self, user_prompt: str, budget_chars: int) -> str:
        if len(user_prompt) <= budget_chars:
            return user_prompt
        try:
            document = json.loads(user_prompt)
        except json.JSONDecodeError as exc:
            raise ContextBudgetError("O prompt excede o contexto e não é truncável.") from exc

        holders = _collect_holders(document)
        # Cada iteração remove o excesso medido; a serialização JSON pode reintroduzir escapes.
        for _ in range(4):
            serialized = json.dumps(document, ensure_ascii=False)
            excess = len(serialized) - budget_chars
            if excess <= 0:
                return serialized
            self._shrink(holders, excess)
        serialized = json.dumps(document, ensure_ascii=False)
        if len(serialized) > budget_chars:
            raise ContextBudgetError("O prompt excede o contexto mesmo após truncar a evidência.")
        return serialized

    def _shrink(self, holders: list[tuple[dict[str, Any], str]], excess: int) -> None:
        lengths = [len(container[key]) for container, key in holders]
        total = sum(lengths)
        reducible = sum(max(0, length - self.min_chunk_chars) for length in lengths)
        if reducible < excess:
            raise ContextBudgetError("O prompt excede o contexto mesmo após truncar a evidência.")
        # Limite comum: trechos curtos ficam intactos e os longos são cortados igualmente.
        low, high = self.min_chunk_chars, max(lengths)
        while low < high:
            cap = (low + high + 1) // 2
            if total - sum(min(length, cap) for length in lengths) >= excess:
                low = cap
            else:
                high = cap - 1
        cap = low
        for container, key in holders:
            container[key] = _truncate(container[key], cap)


def _collect_holders(node: Any) -> list[tuple[dict[str, Any], str]]:
    holders: list[tuple[dict[str, Any], str]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in TRUNCATABLE_KEYS and isinstance(value, str):
                holders.append((node, key))
            else:
                holders.extend(_collect_holders(value))
    elif isinstance(node, list):
        for item in node:
            holders.extend(_collect_holders(item))
    return holders


def _truncate(text: str, cap: int) -> str:
    if len(text) <= cap:
        return text
    keep = max(1, cap - len(TRUNCATION_MARK))
    cut = text[:keep]
    boundary = cut.rfind(" ")
    if boundary > keep // 2:
        cut = cut[:boundary]
    return cut.rstrip() + TRUNCATION_MARK
