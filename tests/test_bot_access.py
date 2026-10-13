from __future__ import annotations

import pytest

from immunocheck.bot_access import (
    AccessConfigurationError,
    AccessPolicy,
    ChatRateLimiter,
)
from immunocheck.telegram import RATE_LIMIT_MESSAGE, TelegramUpdateHandler
from tests.test_telegram import StubClient, StubPipeline, update_with_text


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_limiter_blocks_after_quota_and_recovers_after_window() -> None:
    clock = Clock()
    limiter = ChatRateLimiter(max_messages=2, window_seconds=10, clock=clock)
    assert [limiter.allow(1) for _ in range(3)] == [True, True, False]
    assert limiter.allow(2) is True
    clock.now = 10.0
    assert limiter.allow(1) is True


def test_limiter_notifies_once_per_window_and_bounds_memory() -> None:
    clock = Clock()
    limiter = ChatRateLimiter(max_messages=1, window_seconds=10, clock=clock, max_tracked_chats=3)
    assert limiter.should_notify(1) is True
    assert limiter.should_notify(1) is False
    clock.now = 10.0
    assert limiter.should_notify(1) is True
    for chat in range(10, 20):
        limiter.allow(chat)
        limiter.should_notify(chat)
    assert len(limiter._events) <= 3
    assert len(limiter._notified) <= 3


def test_limiter_rejects_invalid_configuration() -> None:
    with pytest.raises(AccessConfigurationError):
        ChatRateLimiter(max_messages=0)


def test_policy_from_environment() -> None:
    open_policy = AccessPolicy.from_environment({})
    assert open_policy.is_allowed(123) and open_policy.allowed_chat_ids is None
    assert open_policy.limiter.max_messages == 5

    policy = AccessPolicy.from_environment(
        {
            "TELEGRAM_ALLOWED_CHAT_IDS": "10, -20",
            "TELEGRAM_RATE_LIMIT_MESSAGES": "3",
            "TELEGRAM_RATE_LIMIT_WINDOW_SECONDS": "30",
        }
    )
    assert policy.is_allowed(-20) and not policy.is_allowed(99)
    assert (policy.limiter.max_messages, policy.limiter.window_seconds) == (3, 30)

    for bad in (
        {"TELEGRAM_ALLOWED_CHAT_IDS": "abc"},
        {"TELEGRAM_ALLOWED_CHAT_IDS": " , "},
        {"TELEGRAM_RATE_LIMIT_MESSAGES": "x"},
    ):
        with pytest.raises(AccessConfigurationError):
            AccessPolicy.from_environment(bad)


def _handler(policy: AccessPolicy) -> tuple[TelegramUpdateHandler, StubClient]:
    client = StubClient()
    pipeline = StubPipeline(events=client.events)
    return TelegramUpdateHandler(client=client, pipeline=pipeline, access=policy), client


def test_handler_ignores_chats_outside_allowlist() -> None:
    handler, client = _handler(AccessPolicy(allowed_chat_ids=frozenset({999})))
    outcome = handler.handle(update_with_text("Vacinas causam autismo?"))
    assert outcome.accepted_for_analysis is False
    assert client.messages == []


def test_handler_throttles_flooding_chat_with_single_notice() -> None:
    clock = Clock()
    policy = AccessPolicy(limiter=ChatRateLimiter(max_messages=1, window_seconds=60, clock=clock))
    handler, client = _handler(policy)
    assert handler.handle(update_with_text("/ajuda")).accepted_for_analysis is False
    for _ in range(3):
        handler.handle(update_with_text("/ajuda"))
    notices = [text for _, text in client.messages if text == RATE_LIMIT_MESSAGE]
    assert len(notices) == 1


def test_handler_reuses_pipeline_input_limits_unless_overridden() -> None:
    from immunocheck.domain.input_policy import InputLimits

    class Limited(StubPipeline):
        input_limits = InputLimits(max_text_chars=10)

    client = StubClient()
    inherited = TelegramUpdateHandler(client=client, pipeline=Limited(events=[]))
    assert inherited.input_limits.max_text_chars == 10
    explicit = TelegramUpdateHandler(
        client=client, pipeline=Limited(events=[]), input_limits=InputLimits(max_text_chars=20)
    )
    assert explicit.input_limits.max_text_chars == 20
    default = TelegramUpdateHandler(client=client, pipeline=StubPipeline(events=[]))
    assert default.input_limits.max_text_chars == 4_096
