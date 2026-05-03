from __future__ import annotations

import time

from app.vision.gesture_smoothing import GestureSmoothing
from app.vision.gesture_classifier import GestureResult


def _result(name: str, confidence: float = 0.9) -> GestureResult:
    return GestureResult(name=name, confidence=confidence)


def test_not_stable_enough_returns_none():
    smoother = GestureSmoothing(min_stable_frames=5, confidence_threshold=0.75, cooldown_ms=0)
    for _ in range(4):
        r = smoother.update(_result("open_palm"))
    assert r is None


def test_stable_frames_accepted():
    smoother = GestureSmoothing(min_stable_frames=3, confidence_threshold=0.75, cooldown_ms=0)
    r = None
    for _ in range(3):
        r = smoother.update(_result("open_palm"))
    assert r is not None
    assert r.name == "open_palm"


def test_inconsistent_frames_blocked():
    smoother = GestureSmoothing(min_stable_frames=3, confidence_threshold=0.75, cooldown_ms=0)
    smoother.update(_result("open_palm"))
    smoother.update(_result("fist"))
    r = smoother.update(_result("open_palm"))
    assert r is None


def test_low_confidence_blocked():
    smoother = GestureSmoothing(min_stable_frames=3, confidence_threshold=0.75, cooldown_ms=0)
    r = None
    for _ in range(5):
        r = smoother.update(_result("open_palm", confidence=0.5))
    assert r is None


def test_cooldown_prevents_repeat():
    smoother = GestureSmoothing(min_stable_frames=3, confidence_threshold=0.75, cooldown_ms=500)
    # First gesture fires
    for _ in range(3):
        r = smoother.update(_result("open_palm"))
    assert r is not None
    # Immediately after: cooldown blocks
    for _ in range(3):
        r = smoother.update(_result("open_palm"))
    assert r is None


def test_reset_clears_state():
    smoother = GestureSmoothing(min_stable_frames=3, confidence_threshold=0.75, cooldown_ms=0)
    smoother.update(_result("open_palm"))
    smoother.update(_result("open_palm"))
    smoother.reset()
    r = None
    for _ in range(3):
        r = smoother.update(_result("open_palm"))
    assert r is not None
