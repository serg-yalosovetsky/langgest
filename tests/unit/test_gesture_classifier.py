from __future__ import annotations

import numpy as np
import pytest

from app.vision.gesture_classifier import GestureClassifier
from app.vision.mediapipe_hands import (
    HandLandmarks,
    WRIST, THUMB_TIP,
    INDEX_MCP, INDEX_TIP,
    MIDDLE_MCP, MIDDLE_TIP,
    RING_MCP, RING_TIP,
    PINKY_MCP, PINKY_TIP,
)


def _blank_landmarks() -> np.ndarray:
    """21 landmarks at origin."""
    return np.zeros((21, 3), dtype=np.float32)


def _open_palm_landmarks() -> np.ndarray:
    lm = _blank_landmarks()
    for tip, mcp in [(INDEX_TIP, INDEX_MCP), (MIDDLE_TIP, MIDDLE_MCP),
                     (RING_TIP, RING_MCP), (PINKY_TIP, PINKY_MCP)]:
        lm[mcp, 1] = 0.5   # MCP lower (larger y = lower on screen in image coords)
        lm[tip, 1] = 0.2   # tip higher (smaller y)
    lm[THUMB_TIP, 0] = 0.3
    return lm


def _fist_landmarks() -> np.ndarray:
    lm = _blank_landmarks()
    for tip, mcp in [(INDEX_TIP, INDEX_MCP), (MIDDLE_TIP, MIDDLE_MCP),
                     (RING_TIP, RING_MCP), (PINKY_TIP, PINKY_MCP)]:
        lm[mcp, 1] = 0.2   # MCP higher
        lm[tip, 1] = 0.6   # tip lower (curled under)
    return lm


def _pinch_landmarks() -> np.ndarray:
    lm = _blank_landmarks()
    # Thumb tip and index tip very close together
    lm[THUMB_TIP] = [0.5, 0.5, 0.0]
    lm[INDEX_TIP] = [0.52, 0.5, 0.0]  # distance ~0.02 < threshold 0.06
    return lm


def _two_fingers_landmarks() -> np.ndarray:
    lm = _blank_landmarks()
    # Index and middle extended
    lm[INDEX_MCP, 1] = 0.5
    lm[INDEX_TIP, 1] = 0.2
    lm[MIDDLE_MCP, 1] = 0.5
    lm[MIDDLE_TIP, 1] = 0.2
    # Ring and pinky curled
    lm[RING_MCP, 1] = 0.2
    lm[RING_TIP, 1] = 0.6
    lm[PINKY_MCP, 1] = 0.2
    lm[PINKY_TIP, 1] = 0.6
    return lm


def test_open_palm_classified():
    clf = GestureClassifier()
    hand = HandLandmarks(landmarks=_open_palm_landmarks(), handedness="right", score=0.99)
    result = clf.classify(hand)
    assert result is not None
    assert result.name == "open_palm"
    assert result.confidence > 0.8


def test_fist_classified():
    clf = GestureClassifier()
    hand = HandLandmarks(landmarks=_fist_landmarks(), handedness="right", score=0.99)
    result = clf.classify(hand)
    assert result is not None
    assert result.name == "fist"


def test_pinch_classified():
    clf = GestureClassifier()
    hand = HandLandmarks(landmarks=_pinch_landmarks(), handedness="right", score=0.99)
    result = clf.classify(hand)
    assert result is not None
    assert result.name == "pinch"


def test_two_fingers_classified():
    clf = GestureClassifier()
    hand = HandLandmarks(landmarks=_two_fingers_landmarks(), handedness="right", score=0.99)
    result = clf.classify(hand)
    assert result is not None
    assert result.name == "two_fingers"


def test_ambiguous_returns_something_or_none():
    clf = GestureClassifier()
    hand = HandLandmarks(landmarks=_blank_landmarks(), handedness="right", score=0.5)
    # Should not raise
    result = clf.classify(hand)
    # All zeros could match fist (all tips at same y as MCP → not clearly extended)
    # Just verify no crash
