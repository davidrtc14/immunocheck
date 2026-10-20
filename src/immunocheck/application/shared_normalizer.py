"""Normalização feita uma vez por requisição e compartilhada entre as duas etapas da cascata (ADR-055).

Na cascata, a v3 e a `v5_fixed` recebem a mesma entrada. Com imagem ou link, cada uma normalizaria por
conta própria, repetindo o OCR ou o download. Este invólucro guarda o texto normalizado da submissão em
andamento, por identidade do objeto e só na thread atual, e o descarta ao fim da requisição.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Protocol

from immunocheck.application.ports import ContentNormalizer
from immunocheck.domain.models import ContentSubmission, FactCheckResult


class SharedNormalizer:
    def __init__(self, delegate: ContentNormalizer) -> None:
        self._delegate = delegate
        self._local = threading.local()

    def normalize(self, submission: ContentSubmission) -> str:
        cached = getattr(self._local, "entry", None)
        if cached is not None and cached[0] is submission:
            return cached[1]
        text = self._delegate.normalize(submission)
        self._local.entry = (submission, text)
        return text

    def clear(self) -> None:
        self._local.entry = None


class FactCheckRunner(Protocol):
    def run(self, submission: ContentSubmission) -> FactCheckResult: ...


@dataclass(slots=True)
class ClearingRunner:
    """Roda a pipeline e descarta o texto normalizado ao final, mesmo em caso de erro."""

    pipeline: FactCheckRunner
    normalizer: SharedNormalizer

    def run(self, submission: ContentSubmission) -> FactCheckResult:
        try:
            return self.pipeline.run(submission)
        finally:
            self.normalizer.clear()
