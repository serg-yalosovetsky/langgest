from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IntentSource(str, Enum):
    VOICE = "voice"
    GESTURE = "gesture"
    FUSED = "fused"
    MACRO = "macro"


class RiskLevel(str, Enum):
    SAFE = "safe"
    MEDIUM = "medium"
    DANGEROUS = "dangerous"
    FORBIDDEN = "forbidden"


@dataclass
class Intent:
    id: str
    source: IntentSource
    confidence: float = 1.0
    language: str = "ru"
    text: str = ""
    slots: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source.value,
            "confidence": self.confidence,
            "language": self.language,
            "text": self.text,
            "slots": self.slots,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_gesture(cls, gesture_name: str, confidence: float = 1.0) -> "Intent":
        gesture_intent_map = {
            "open_palm": "media.play_pause",
            "fist": "action.cancel",
            "swipe_left": "media.previous",
            "swipe_right": "media.next",
            "hand_up": "volume.up",
            "hand_down": "volume.down",
            "pinch": "action.click",
            "two_fingers": "action.scroll_mode",
        }
        intent_id = gesture_intent_map.get(gesture_name, f"gesture.{gesture_name}")
        return cls(
            id=intent_id,
            source=IntentSource.GESTURE,
            confidence=confidence,
            slots={"gesture": gesture_name},
        )
