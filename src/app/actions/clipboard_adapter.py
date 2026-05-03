from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def copy() -> bool:
    from app.actions.windows_adapter import send_hotkey
    return send_hotkey("ctrl", "c")


def cut() -> bool:
    from app.actions.windows_adapter import send_hotkey
    return send_hotkey("ctrl", "x")


def paste() -> bool:
    from app.actions.windows_adapter import send_hotkey
    return send_hotkey("ctrl", "v")


def clear() -> bool:
    try:
        import pyperclip  # type: ignore

        pyperclip.copy("")
        logger.debug("Clipboard cleared")
        return True
    except ImportError:
        logger.warning("pyperclip not installed — clipboard clear unavailable")
        return False
    except Exception as e:
        logger.error("clipboard clear error: %s", e)
        return False


def read() -> tuple[str, int]:
    """Return (preview_text, length). Never logs raw content."""
    try:
        import pyperclip  # type: ignore

        content = pyperclip.paste() or ""
        length = len(content)
        preview = content[:50] + "..." if length > 50 else content
        logger.debug("Clipboard read: length=%d", length)
        return preview, length
    except ImportError:
        logger.warning("pyperclip not installed")
        return "", 0
    except Exception as e:
        logger.error("clipboard read error: %s", e)
        return "", 0
