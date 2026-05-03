from __future__ import annotations

import queue
import threading
from dataclasses import dataclass, field
from typing import Any, Generator


@dataclass
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Thread-safe event queue. Producers call post(); main loop calls listen()."""

    def __init__(self, maxsize: int = 256) -> None:
        self._queue: queue.Queue[Event | None] = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()

    def post(self, event: Event) -> None:
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            # Drop oldest event to make room
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            self._queue.put_nowait(event)

    def listen(self, timeout: float = 0.1) -> Generator[Event, None, None]:
        """Yield events forever. Yields nothing on timeout (allows caller to check shutdown)."""
        while True:
            try:
                event = self._queue.get(timeout=timeout)
                if event is None:
                    break
                yield event
            except queue.Empty:
                continue

    def stop(self) -> None:
        self._queue.put(None)
