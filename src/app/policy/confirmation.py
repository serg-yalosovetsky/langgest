from __future__ import annotations

import logging
import threading
import time
from typing import Callable

from app.nlu.intent import Intent

logger = logging.getLogger(__name__)

CONFIRMATION_TIMEOUT_S = 30.0
CONFIRMATION_PHRASES_RU = frozenset(["подтверждаю", "да", "выполни", "ок", "yes"])
CONFIRMATION_PHRASES_EN = frozenset(["confirm", "yes", "do it", "proceed", "ok"])


class ConfirmationManager:
    """
    Holds a pending intent awaiting user confirmation.
    Confirmation is provided either by voice (another voice.text event with confirm phrase)
    or by UI button.
    """

    def __init__(self, on_confirmed: Callable[[Intent], None], on_cancelled: Callable[[Intent], None]) -> None:
        self._on_confirmed = on_confirmed
        self._on_cancelled = on_cancelled
        self._pending: Intent | None = None
        self._pending_time: float = 0.0
        self._lock = threading.Lock()

    def request(self, intent: Intent) -> None:
        with self._lock:
            self._pending = intent
            self._pending_time = time.monotonic()
        logger.info("Confirmation requested for intent: %s", intent.id)

    def try_confirm(self, text: str, language: str) -> bool:
        """Returns True if the text matches a confirmation phrase and confirmation was pending."""
        phrases = CONFIRMATION_PHRASES_RU if language == "ru" else CONFIRMATION_PHRASES_EN
        normalized = text.strip().lower()
        if normalized not in phrases:
            return False

        with self._lock:
            if self._pending is None:
                return False
            if time.monotonic() - self._pending_time > CONFIRMATION_TIMEOUT_S:
                logger.info("Confirmation timed out for: %s", self._pending.id)
                self._pending = None
                return False
            intent = self._pending
            self._pending = None

        logger.info("Confirmation accepted for: %s", intent.id)
        self._on_confirmed(intent)
        return True

    def cancel(self) -> None:
        with self._lock:
            if self._pending:
                intent = self._pending
                self._pending = None
                self._on_cancelled(intent)

    def has_pending(self) -> bool:
        with self._lock:
            if self._pending is None:
                return False
            if time.monotonic() - self._pending_time > CONFIRMATION_TIMEOUT_S:
                self._pending = None
                return False
            return True
