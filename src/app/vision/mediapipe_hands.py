from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# MediaPipe landmark indices
WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_MCP = 13
RING_TIP = 16
PINKY_MCP = 17
PINKY_TIP = 20


@dataclass
class HandLandmarks:
    landmarks: "np.ndarray"  # shape (21, 3) normalized [0,1]
    handedness: str  # "left" | "right"
    score: float = 1.0


class MPHandsDetector:
    """MediaPipe Hands wrapper. Returns HandLandmarks per detected hand."""

    def __init__(self, max_hands: int = 1, min_detection_confidence: float = 0.7) -> None:
        self._hands = None
        self._available = False
        self._max_hands = max_hands
        self._min_conf = min_detection_confidence
        self._load()

    def _load(self) -> None:
        try:
            import mediapipe as mp  # type: ignore

            self._mp_hands = mp.solutions.hands
            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self._max_hands,
                min_detection_confidence=self._min_conf,
                min_tracking_confidence=0.5,
            )
            self._available = True
            logger.info("MediaPipe Hands loaded")
        except ImportError:
            logger.warning("mediapipe not installed — gesture recognition unavailable")
        except Exception as e:
            logger.error("Failed to load MediaPipe Hands: %s", e)

    def detect(self, frame_rgb: "np.ndarray") -> list[HandLandmarks]:
        if not self._available or self._hands is None:
            return []
        try:
            import numpy as np

            results = self._hands.process(frame_rgb)
            if not results.multi_hand_landmarks:
                return []

            detections: list[HandLandmarks] = []
            for hand_lm, hand_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness,
            ):
                lm_array = np.array(
                    [[lm.x, lm.y, lm.z] for lm in hand_lm.landmark],
                    dtype=np.float32,
                )
                handedness = hand_info.classification[0].label.lower()
                score = hand_info.classification[0].score
                detections.append(HandLandmarks(lm_array, handedness, score))
            return detections
        except Exception as e:
            logger.error("MPHandsDetector.detect error: %s", e)
            return []

    def is_available(self) -> bool:
        return self._available

    def close(self) -> None:
        if self._hands:
            self._hands.close()
