from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

from app.vision.mediapipe_hands import (
    HandLandmarks,
    WRIST,
    THUMB_TIP,
    INDEX_MCP, INDEX_TIP,
    MIDDLE_MCP, MIDDLE_TIP,
    RING_MCP, RING_TIP,
    PINKY_MCP, PINKY_TIP,
)

logger = logging.getLogger(__name__)

PINCH_THRESHOLD = 0.06


@dataclass
class GestureResult:
    name: str
    confidence: float


class GestureClassifier:
    """Heuristic gesture classifier using MediaPipe hand landmarks."""

    def classify(self, hand: HandLandmarks) -> GestureResult | None:
        lm = hand.landmarks
        try:
            if self._is_open_palm(lm):
                return GestureResult("open_palm", 0.9)
            if self._is_fist(lm):
                return GestureResult("fist", 0.9)
            if self._is_pinch(lm):
                return GestureResult("pinch", 0.85)
            if self._is_two_fingers(lm):
                return GestureResult("two_fingers", 0.85)
        except Exception as e:
            logger.debug("GestureClassifier error: %s", e)
        return None

    def _is_open_palm(self, lm: "np.ndarray") -> bool:
        pairs = [
            (INDEX_TIP, INDEX_MCP),
            (MIDDLE_TIP, MIDDLE_MCP),
            (RING_TIP, RING_MCP),
            (PINKY_TIP, PINKY_MCP),
        ]
        extended = sum(1 for tip, mcp in pairs if lm[tip, 1] < lm[mcp, 1])
        return extended >= 4

    def _is_fist(self, lm: "np.ndarray") -> bool:
        pairs = [
            (INDEX_TIP, INDEX_MCP),
            (MIDDLE_TIP, MIDDLE_MCP),
            (RING_TIP, RING_MCP),
            (PINKY_TIP, PINKY_MCP),
        ]
        curled = sum(1 for tip, mcp in pairs if lm[tip, 1] > lm[mcp, 1])
        return curled >= 4

    def _is_pinch(self, lm: "np.ndarray") -> bool:
        import numpy as np

        dist = float(np.linalg.norm(lm[THUMB_TIP] - lm[INDEX_TIP]))
        return dist < PINCH_THRESHOLD

    def _is_two_fingers(self, lm: "np.ndarray") -> bool:
        index_up = lm[INDEX_TIP, 1] < lm[INDEX_MCP, 1]
        middle_up = lm[MIDDLE_TIP, 1] < lm[MIDDLE_MCP, 1]
        ring_down = lm[RING_TIP, 1] > lm[RING_MCP, 1]
        pinky_down = lm[PINKY_TIP, 1] > lm[PINKY_MCP, 1]
        return index_up and middle_up and ring_down and pinky_down
