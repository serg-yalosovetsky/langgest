from __future__ import annotations

import logging

from app.actions.windows_adapter import send_hotkey, type_text, send_keypress, open_app

logger = logging.getLogger(__name__)


def search(query: str) -> bool:
    """Focus address bar and type search query."""
    if not send_hotkey("ctrl", "l"):
        return False
    import time
    time.sleep(0.15)
    if not type_text(query):
        return False
    return send_keypress("enter")
