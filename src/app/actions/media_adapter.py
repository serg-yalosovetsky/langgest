from __future__ import annotations

import logging

from app.actions.windows_adapter import send_hotkey, send_keypress

logger = logging.getLogger(__name__)


def play_pause() -> bool:
    return send_keypress("playpause")


def next_track() -> bool:
    return send_keypress("nexttrack")


def previous_track() -> bool:
    return send_keypress("prevtrack")


def stop() -> bool:
    return send_keypress("stop")
