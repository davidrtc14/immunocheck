"""v7 (ADR-054), candidata C4: queda para a v3 quando a decomposição falha.

A v5 já tenta a decomposição de novo com instrução de reparo. Se a segunda tentativa também falhar,
ela abstém por falha técnica antes de existir a alegação canônica. Com a C4, esse caso roda na v3
em vez de abster. Falhas depois da decomposição (no juiz) continuam como abstenção técnica.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any, Protocol

from immunocheck.application.v7_verdict import V7FactCheckPipeline
from immunocheck.domain.models import ContentSubmission, FactCheckResult

FALLBACK_LABEL = "v3"


class FactCheckRunner(Protocol):
    def run(self, submission: ContentSubmission) -> FactCheckResult: ...


def decomposition_failed(trace: dict[str, Any]) -> bool:
    return bool(trace.get("technical_abstention")) and "canonical" not in trace


class DecompositionFallbackPipeline:
    """Roda a v7 e, se a decomposição falhar duas vezes, devolve o resultado da v3."""

    def __init__(
        self,
        primary: V7FactCheckPipeline,
        fallback_factory: Callable[[], FactCheckRunner],
        trace_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._traces: list[dict[str, Any]] = []
        self.primary = dataclasses.replace(primary, trace_sink=self._traces.append)
        self._fallback_factory = fallback_factory
        self._fallback: FactCheckRunner | None = None
        self.trace_sink = trace_sink

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self._traces.clear()
        result = self.primary.run(submission)
        trace = self._traces[-1] if self._traces else {}
        failed = decomposition_failed(trace)
        if failed:
            trace = trace | {
                "technical_abstention": False,
                "decomposition_fallback": FALLBACK_LABEL,
            }
        if self.trace_sink is not None:
            # Antes da v3, para que o trace fique registrado mesmo se ela lançar exceção.
            self.trace_sink(trace)
        return self._fallback_runner().run(submission) if failed else result

    def _fallback_runner(self) -> FactCheckRunner:
        # A v3 carrega o próprio retriever; só é montada se alguma decomposição falhar.
        if self._fallback is None:
            self._fallback = self._fallback_factory()
        return self._fallback
