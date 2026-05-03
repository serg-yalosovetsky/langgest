from __future__ import annotations

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


def send_hotkey(*keys: str) -> bool:
    """Send a hotkey combination. Returns True on success."""
    try:
        import pyautogui  # type: ignore

        pyautogui.hotkey(*keys)
        logger.debug("Hotkey: %s", "+".join(keys))
        return True
    except ImportError:
        logger.warning("pyautogui not installed — hotkey skipped: %s", keys)
        return False
    except Exception as e:
        logger.error("Hotkey error %s: %s", keys, e)
        return False


def send_keypress(key: str) -> bool:
    try:
        import pyautogui  # type: ignore

        pyautogui.press(key)
        logger.debug("Keypress: %s", key)
        return True
    except ImportError:
        logger.warning("pyautogui not installed — keypress skipped: %s", key)
        return False
    except Exception as e:
        logger.error("Keypress error %s: %s", key, e)
        return False


def type_text(text: str) -> bool:
    try:
        import pyautogui  # type: ignore

        pyautogui.typewrite(text, interval=0.02)
        logger.debug("Typed text length=%d", len(text))
        return True
    except ImportError:
        logger.warning("pyautogui not installed — type_text skipped")
        return False
    except Exception as e:
        logger.error("type_text error: %s", e)
        return False


def open_app(app: str) -> bool:
    try:
        import subprocess

        subprocess.Popen([app], shell=True)
        logger.debug("Opened app: %s", app)
        return True
    except Exception as e:
        logger.error("open_app error %s: %s", app, e)
        return False


def open_url(url: str) -> bool:
    try:
        import webbrowser

        webbrowser.open(url)
        logger.debug("Opened URL: %s", url)
        return True
    except Exception as e:
        logger.error("open_url error: %s", e)
        return False


def activate_window_by_process(process_names: list[str]) -> bool:
    """Bring window of first matching process to foreground (Windows only)."""
    try:
        import ctypes

        user32 = ctypes.windll.user32  # type: ignore

        def enum_callback(hwnd, _):
            if not user32.IsWindowVisible(hwnd):
                return True
            pid_val = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_val))
            try:
                import psutil  # type: ignore

                proc = psutil.Process(pid_val.value)
                if proc.name().lower() in [p.lower() for p in process_names]:
                    user32.SetForegroundWindow(hwnd)
                    return False
            except Exception:
                pass
            return True

        import ctypes.wintypes

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
        return True
    except AttributeError:
        logger.debug("activate_window_by_process: not on Windows")
        return False
    except Exception as e:
        logger.error("activate_window error: %s", e)
        return False
