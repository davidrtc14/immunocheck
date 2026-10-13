from __future__ import annotations

import time
from collections import OrderedDict, deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

ALLOWLIST_VARIABLE = "TELEGRAM_ALLOWED_CHAT_IDS"
RATE_LIMIT_MESSAGES_VARIABLE = "TELEGRAM_RATE_LIMIT_MESSAGES"
RATE_LIMIT_WINDOW_VARIABLE = "TELEGRAM_RATE_LIMIT_WINDOW_SECONDS"
DEFAULT_RATE_LIMIT_MESSAGES = 5
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60.0
MAX_TRACKED_CHATS = 10_000


class AccessConfigurationError(ValueError):
    """Configuração inválida de controle de acesso do bot."""


@dataclass(slots=True)
class ChatRateLimiter:
    """Janela deslizante por chat, somente em memória: nada é gravado em disco ou log."""

    max_messages: int = DEFAULT_RATE_LIMIT_MESSAGES
    window_seconds: float = DEFAULT_RATE_LIMIT_WINDOW_SECONDS
    clock: Callable[[], float] = time.monotonic
    max_tracked_chats: int = MAX_TRACKED_CHATS
    _events: OrderedDict[int, deque[float]] = field(
        default_factory=OrderedDict, init=False, repr=False
    )
    _notified: OrderedDict[int, float] = field(
        default_factory=OrderedDict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.max_messages <= 0 or self.window_seconds <= 0 or self.max_tracked_chats <= 0:
            raise AccessConfigurationError("Limites de taxa devem ser positivos.")

    def allow(self, chat_id: int) -> bool:
        """Registra a tentativa se ela couber na janela deslizante."""
        now = self.clock()
        events = self._events.pop(chat_id, None) or deque()
        while events and now - events[0] >= self.window_seconds:
            events.popleft()
        allowed = len(events) < self.max_messages
        if allowed:
            events.append(now)
        self._events[chat_id] = events
        while len(self._events) > self.max_tracked_chats:
            self._events.popitem(last=False)
        return allowed

    def should_notify(self, chat_id: int) -> bool:
        """Evita amplificação: avisa o chat bloqueado no máximo uma vez por janela."""
        now = self.clock()
        last = self._notified.pop(chat_id, None)
        notify = last is None or now - last >= self.window_seconds
        self._notified[chat_id] = now if notify else last
        while len(self._notified) > self.max_tracked_chats:
            self._notified.popitem(last=False)
        return notify


@dataclass(frozen=True, slots=True)
class AccessPolicy:
    allowed_chat_ids: frozenset[int] | None = None
    limiter: ChatRateLimiter = field(default_factory=ChatRateLimiter)

    def is_allowed(self, chat_id: int) -> bool:
        return self.allowed_chat_ids is None or chat_id in self.allowed_chat_ids

    @classmethod
    def from_environment(cls, environ: Mapping[str, str]) -> AccessPolicy:
        raw_allowlist = environ.get(ALLOWLIST_VARIABLE, "").strip()
        allowlist: frozenset[int] | None = None
        if raw_allowlist:
            try:
                allowlist = frozenset(int(item) for item in raw_allowlist.split(",") if item.strip())
            except ValueError as exc:
                raise AccessConfigurationError(
                    f"{ALLOWLIST_VARIABLE} deve conter IDs inteiros separados por vírgula."
                ) from exc
            if not allowlist:
                raise AccessConfigurationError(f"{ALLOWLIST_VARIABLE} não contém IDs válidos.")
        try:
            messages = int(
                environ.get(RATE_LIMIT_MESSAGES_VARIABLE, DEFAULT_RATE_LIMIT_MESSAGES)
            )
            window = float(
                environ.get(RATE_LIMIT_WINDOW_VARIABLE, DEFAULT_RATE_LIMIT_WINDOW_SECONDS)
            )
        except ValueError as exc:
            raise AccessConfigurationError("Limites de taxa devem ser numéricos.") from exc
        return cls(allowed_chat_ids=allowlist, limiter=ChatRateLimiter(messages, window))
