from __future__ import annotations

import time

import pytest

from app.fusion.fusion_engine import FusionEngine, SAFE_GESTURE_INTENTS
from app.nlu.intent import Intent, IntentSource


def _voice(intent_id: str, text: str = "", confidence: float = 0.95) -> Intent:
    return Intent(id=intent_id, source=IntentSource.VOICE, confidence=confidence, text=text)


def _gesture(gesture_name: str, confidence: float = 0.9) -> Intent:
    return Intent(
        id=Intent.from_gesture(gesture_name).id,
        source=IntentSource.GESTURE,
        confidence=confidence,
        slots={"gesture": gesture_name},
    )


def test_voice_alone_passes_through():
    engine = FusionEngine()
    intent = _voice("volume.up")
    result = engine.add(intent)
    assert result is not None
    assert result.id == "volume.up"
    assert result.source == IntentSource.VOICE


def test_safe_gesture_alone_passes():
    engine = FusionEngine()
    g = _gesture("open_palm")
    assert g.id in SAFE_GESTURE_INTENTS
    result = engine.add(g)
    assert result is not None
    assert result.id == "media.play_pause"


def test_unsafe_gesture_alone_blocked():
    engine = FusionEngine()
    g = _gesture("pinch")  # action.click — not in safe list
    result = engine.add(g)
    assert result is None


def test_voice_wins_on_conflict():
    engine = FusionEngine()
    voice = _voice("browser.open_tab", text="открой вкладку")
    engine.add(voice)
    # Gesture arrives right after — no fusion rule matches
    g = _gesture("pinch")
    result = engine.add(g)
    # gesture alone after voice with no matching fusion rule → blocked
    assert result is None


def test_fusion_volume_hand_up():
    engine = FusionEngine()
    voice = _voice("volume.up", text="volume")
    engine.add(voice)

    g = _gesture("hand_up")
    result = engine.add(g)
    assert result is not None
    assert result.id == "volume.up"
    assert result.source == IntentSource.FUSED


def test_fusion_scroll_down():
    engine = FusionEngine()
    voice = _voice("action.scroll", text="прокрути")
    engine.add(voice)

    g = _gesture("hand_down")
    result = engine.add(g)
    assert result is not None
    assert result.id == "action.scroll_down"
    assert result.source == IntentSource.FUSED


def test_gesture_before_voice_fused():
    engine = FusionEngine()
    g = _gesture("hand_up")
    engine.add(g)  # gesture first — blocked (not safe standalone)

    voice = _voice("volume.up", text="volume")
    result = engine.add(voice)
    # Voice arrived within window after gesture → fusion attempted
    assert result is not None
