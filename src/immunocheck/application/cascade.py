"""Condição C6 da Fase 20 (ADR-055): cascata v3 → `v5_fixed`.

A v3 responde primeiro. Só quando ela sustenta a alegação (`SUPPORTED`) a `v5_fixed` roda sobre a mesma
entrada, como verificação independente; se a verificação não sustentar, vale a resposta dela. Nos
demais casos, vale a resposta da v3. Nenhuma das duas pipelines é alterada.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from immunocheck.domain.models import ContentSubmission, FactCheckResult, Verdict


class FactCheckRunner(Protocol):
    def run(self, submission: ContentSubmission) -> FactCheckResult: ...


@dataclass(slots=True)
class SupportedVerificationCascade:
    primary: FactCheckRunner
    verifier: FactCheckRunner
    trace_sink: Callable[[dict[str, Any]], None] | None = None
    verifier_traces: list[dict[str, Any]] = field(default_factory=list)

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        self.verifier_traces.clear()
        first = self.primary.run(submission)
        trace: dict[str, Any] = {"primary_verdict": first.verdict.value, "verified": False}
        result = first
        if first.verdict is Verdict.SUPPORTED:
            second = self.verifier.run(submission)
            trace.update(
                verified=True,
                verifier_verdict=second.verdict.value,
                verifier_trace=self.verifier_traces[-1] if self.verifier_traces else None,
            )
            if second.verdict is not Verdict.SUPPORTED:
                result = second
        trace["final_verdict"] = result.verdict.value
        if self.trace_sink is not None:
            self.trace_sink(trace)
        return result
