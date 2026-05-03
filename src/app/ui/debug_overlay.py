from __future__ import annotations

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

MAX_ENTRIES = 50


class DebugOverlay:
    """Maintains a ring buffer of recent events for debug display."""

    def __init__(self, max_entries: int = MAX_ENTRIES) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def add(self, entry: dict[str, Any]) -> None:
        self._entries.appendleft(entry)

    def get_recent(self, n: int = 10) -> list[dict[str, Any]]:
        return list(self._entries)[:n]

    def print_recent(self, n: int = 10) -> None:
        import json

        print("\n=== Debug Overlay (last %d events) ===" % n)
        for entry in self.get_recent(n):
            print(json.dumps(entry, ensure_ascii=False, default=str))
