from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from app.nlu.intent import Intent

logger = logging.getLogger(__name__)


class EventLog:
    """JSONL event logger. Redacts sensitive data (clipboard, audio, video)."""

    def __init__(
        self,
        log_path: str | Path = "data/events.jsonl",
        log_clipboard_content: bool = False,
    ) -> None:
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._log_clipboard = log_clipboard_content
        self._lock = threading.Lock()

    def log_intent(
        self,
        intent: Intent,
        active_app: str = "",
        result: str = "success",
        error: str = "",
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(intent.timestamp)),
            "source": intent.source.value,
            "language": intent.language,
            "text": intent.text,
            "intent": intent.id,
            "confidence": round(intent.confidence, 4),
            "active_app": active_app,
            "slots": self._redact_slots(intent.id, intent.slots),
            "result": result,
        }
        if error:
            entry["error"] = error
        self._write(entry)

    def log_blocked(self, intent: Intent, reason: str) -> None:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(intent.timestamp)),
            "event": "blocked",
            "intent": intent.id,
            "reason": reason,
            "confidence": round(intent.confidence, 4),
        }
        self._write(entry)

    def log_confirmation_requested(self, intent: Intent) -> None:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": "confirmation_requested",
            "intent": intent.id,
        }
        self._write(entry)

    def log_gesture(self, gesture_name: str, confidence: float, accepted: bool) -> None:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": "gesture",
            "gesture": gesture_name,
            "confidence": round(confidence, 4),
            "accepted": accepted,
        }
        self._write(entry)

    def log_clipboard_event(self, action: str, content_length: int) -> None:
        entry: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": f"clipboard.{action}",
            "content_preview": "[redacted]",
            "length": content_length,
        }
        self._write(entry)

    def _redact_slots(self, intent_id: str, slots: dict[str, Any]) -> dict[str, Any]:
        if not self._log_clipboard and "clipboard" in intent_id:
            return {"[redacted]": True}
        return slots

    def _write(self, entry: dict[str, Any]) -> None:
        line = json.dumps(entry, ensure_ascii=False)
        with self._lock:
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except OSError as e:
                logger.warning("Failed to write event log: %s", e)
