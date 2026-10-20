from __future__ import annotations

import pytest

from immunocheck import bootstrap_bot
from immunocheck.application.cascade import SupportedVerificationCascade
from immunocheck.application.shared_normalizer import ClearingRunner, SharedNormalizer
from immunocheck.application.tolerant_verification import TolerantPropositionJudge
from immunocheck.domain.models import ContentKind, ContentSubmission, FactCheckResult, Verdict


def test_v7_is_the_default_and_unknown_versions_fail(monkeypatch) -> None:
    monkeypatch.delenv("PIPELINE_VERSION", raising=False)
    assert bootstrap_bot.resolve_pipeline_version(None) == "v7"
    assert bootstrap_bot.resolve_pipeline_version(" V3 ") == "v3"
    monkeypatch.setenv("PIPELINE_VERSION", "v5")
    assert bootstrap_bot.resolve_pipeline_version(None) == "v5"
    with pytest.raises(ValueError):
        bootstrap_bot.resolve_pipeline_version("v6")


def test_older_versions_are_delegated_unchanged(monkeypatch) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(
        bootstrap_bot, "build_configured_text_pipeline", lambda **kw: calls.append(kw) or "v3"
    )
    monkeypatch.setattr(
        bootstrap_bot,
        "build_configured_multimodal_pipeline",
        lambda **kw: calls.append(kw) or "v3-mm",
    )
    assert bootstrap_bot.build_bot_text_pipeline(pipeline_version="v3") == "v3"
    assert bootstrap_bot.build_bot_multimodal_pipeline(pipeline_version="v1") == "v3-mm"
    assert [call["pipeline_version"] for call in calls] == ["v3", "v1"]


class _Judge:
    client, max_output_tokens = object(), 900


class _Pipeline:
    """Imita as dataclasses das pipelines: `dataclasses.replace` troca normalizador e juiz."""

    def __init__(self, normalizer=None, judge=None) -> None:
        self.normalizer, self.judge = normalizer, judge or _Judge()


def _fake_replace(obj, **changes):
    return _Pipeline(changes.get("normalizer", obj.normalizer), changes.get("judge", obj.judge))


def test_v7_text_is_v3_then_v5_fixed(monkeypatch) -> None:
    monkeypatch.setattr(bootstrap_bot.dataclasses, "replace", _fake_replace)
    monkeypatch.setattr(bootstrap_bot, "build_routed_text_pipeline", lambda **kw: "v3")
    monkeypatch.setattr(bootstrap_bot, "build_v5_text_pipeline", lambda **kw: _Pipeline())
    cascade = bootstrap_bot.build_bot_text_pipeline(pipeline_version="v7")
    assert isinstance(cascade, SupportedVerificationCascade) and cascade.primary == "v3"
    assert isinstance(cascade.verifier.judge, TolerantPropositionJudge)


def test_v7_multimodal_shares_one_normalizer(monkeypatch) -> None:
    monkeypatch.setattr(bootstrap_bot.dataclasses, "replace", _fake_replace)
    ocr = object()
    monkeypatch.setattr(bootstrap_bot, "resolve_extraction_version", lambda value=None: "v1")
    monkeypatch.setattr(
        bootstrap_bot, "build_routed_multimodal_pipeline", lambda **kw: _Pipeline(ocr)
    )
    monkeypatch.setattr(bootstrap_bot, "build_v5_multimodal_pipeline", lambda **kw: _Pipeline("v5"))
    runner = bootstrap_bot.build_bot_multimodal_pipeline(pipeline_version="v7")
    assert isinstance(runner, ClearingRunner)
    cascade = runner.pipeline
    shared = cascade.primary.normalizer
    assert isinstance(shared, SharedNormalizer) and cascade.verifier.normalizer is shared
    assert shared._delegate is ocr


class _CountingNormalizer:
    def __init__(self) -> None:
        self.calls = 0

    def normalize(self, submission: ContentSubmission) -> str:
        self.calls += 1
        return f"texto {self.calls}"


def test_shared_normalizer_runs_once_per_submission_and_clears() -> None:
    delegate = _CountingNormalizer()
    shared = SharedNormalizer(delegate)
    first = ContentSubmission(kind=ContentKind.TEXT, text="a")
    assert shared.normalize(first) == shared.normalize(first) == "texto 1"
    second = ContentSubmission(kind=ContentKind.TEXT, text="a")
    assert shared.normalize(second) == "texto 2"
    shared.clear()
    assert shared.normalize(second) == "texto 3" and delegate.calls == 3


def test_clearing_runner_clears_even_on_error() -> None:
    delegate = _CountingNormalizer()
    shared = SharedNormalizer(delegate)
    submission = ContentSubmission(kind=ContentKind.TEXT, text="a")

    class _Failing:
        def run(self, sub):
            shared.normalize(sub)
            raise RuntimeError("falha")

    class _Ok:
        def run(self, sub):
            shared.normalize(sub)
            return FactCheckResult(verdict=Verdict.SUPPORTED, explanation="ok")

    with pytest.raises(RuntimeError):
        ClearingRunner(_Failing(), shared).run(submission)
    assert ClearingRunner(_Ok(), shared).run(submission).verdict is Verdict.SUPPORTED
    assert delegate.calls == 2
