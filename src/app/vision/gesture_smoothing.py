from __future__ import annotations

import time
from collections import deque

from app.vision.gesture_classifier import GestureResult


class GestureSmoothing:
    """
    Anti-false-positive filter:
      - gesture must be stable for min_stable_frames
      - confidence must exceed threshold
      - cooldown_ms must have elapsed since last accepted gesture
    """

    def __init__(
        self,
        min_stable_frames: int = 5,
        confidence_threshold: float = 0.75,
        cooldown_ms: int = 700,
    ) -> None:
        self._min_stable = min_stable_frames
        self._threshold = confidence_threshold
        self._cooldown_s = cooldown_ms / 1000.0
        self._history: deque[str | None] = deque(maxlen=min_stable_frames)
        self._last_accepted: float = 0.0
        self._last_gesture: str | None = None

    def update(self, result: GestureResult | None) -> GestureResult | None:
        name = result.name if result and result.confidence >= self._threshold else None
        self._history.append(name)

        if len(self._history) < self._min_stable:
            return None

        # All frames in history must agree
        if len(set(self._history)) != 1 or name is None:
            return None

        now = time.monotonic()
        if now - self._last_accepted < self._cooldown_s:
            return None

        # Avoid re-triggering the same gesture continuously
        if name == self._last_gesture and now - self._last_accepted < 1.5:
            return None

        self._last_accepted = now
        self._last_gesture = name
        self._history.clear()
        return result

    def reset(self) -> None:
        self._history.clear()
        self._last_gesture = None
