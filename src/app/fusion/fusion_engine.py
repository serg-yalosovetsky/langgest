from __future__ import annotations

import time
from typing import Optional

from app.nlu.intent import Intent, IntentSource

FUSION_WINDOW_S = 1.5

# Gestures that can fire without a voice command
SAFE_GESTURE_INTENTS = frozenset([
    "media.play_pause",
    "media.next",
    "media.previous",
    "volume.up",
    "volume.down",
    "action.cancel",
])

# Voice+gesture combinations: (voice_prefix, gesture_name) -> fused_intent_id
FUSION_RULES: dict[tuple[str, str], str] = {
    ("volume", "hand_up"): "volume.up",
    ("volume", "hand_down"): "volume.down",
    ("прокрути", "hand_down"): "action.scroll_down",
    ("прокрути", "hand_up"): "action.scroll_up",
    ("scroll", "hand_down"): "action.scroll_down",
    ("scroll", "hand_up"): "action.scroll_up",
    ("выбери", "pinch"): "action.click",
    ("select", "pinch"): "action.click",
}


class FusionEngine:
    """
    Combines voice and gesture intents that arrive within FUSION_WINDOW_S.
    Rules:
      - voice + gesture within window → check FUSION_RULES; if matched return fused intent
      - voice alone → return as-is
      - gesture alone → return only if intent is in SAFE_GESTURE_INTENTS
      - conflict (both voice and gesture, no fusion rule) → voice wins
    """

    def __init__(self) -> None:
        self._last_voice: Optional[Intent] = None
        self._last_gesture: Optional[Intent] = None

    def add(self, intent: Intent) -> Optional[Intent]:
        now = time.monotonic()

        if intent.source == IntentSource.VOICE:
            self._last_voice = intent
            # Check if a gesture arrived just before
            if (
                self._last_gesture is not None
                and now - self._last_gesture.timestamp <= FUSION_WINDOW_S
            ):
                fused = self._try_fuse(intent, self._last_gesture)
                if fused:
                    self._last_gesture = None
                    return fused
            return intent

        if intent.source == IntentSource.GESTURE:
            self._last_gesture = intent
            # Check if a voice command arrived just before
            if (
                self._last_voice is not None
                and now - self._last_voice.timestamp <= FUSION_WINDOW_S
            ):
                fused = self._try_fuse(self._last_voice, intent)
                if fused:
                    self._last_voice = None
                    return fused
                # Voice wins on conflict
                return None

            # Gesture alone: only safe gestures are auto-executed
            if intent.id in SAFE_GESTURE_INTENTS:
                return intent
            return None

        # FUSED or MACRO pass through directly
        return intent

    @staticmethod
    def _try_fuse(voice: Intent, gesture: Intent) -> Optional[Intent]:
        gesture_name = gesture.slots.get("gesture", "")
        voice_text = voice.text.lower()

        for (voice_prefix, g_name), fused_id in FUSION_RULES.items():
            if voice_prefix in voice_text and g_name == gesture_name:
                return Intent(
                    id=fused_id,
                    source=IntentSource.FUSED,
                    confidence=min(voice.confidence, gesture.confidence),
                    language=voice.language,
                    text=voice.text,
                    slots={**voice.slots, **gesture.slots},
                )
        return None
