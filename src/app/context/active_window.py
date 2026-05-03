from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    title: str = ""
    process_name: str = ""
    pid: int = 0


def get_active_window() -> WindowInfo:
    """Return info about the currently focused window. Windows-only; gracefully degrades."""
    try:
        import ctypes
        import ctypes.wintypes as wt

        user32 = ctypes.windll.user32  # type: ignore
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return WindowInfo()

        # Get window title
        length = user32.GetWindowTextLengthW(hwnd) + 1
        buf = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buf, length)
        title = buf.value

        # Get process name
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process_name = _get_process_name(pid.value)

        return WindowInfo(title=title, process_name=process_name, pid=pid.value)
    except AttributeError:
        # Not on Windows
        return WindowInfo()
    except Exception as e:
        logger.debug("get_active_window error: %s", e)
        return WindowInfo()


def _get_process_name(pid: int) -> str:
    try:
        import ctypes
        import ctypes.wintypes as wt

        kernel32 = ctypes.windll.kernel32  # type: ignore
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not handle:
            return ""

        psapi = ctypes.windll.psapi  # type: ignore
        buf = ctypes.create_unicode_buffer(260)
        psapi.GetModuleFileNameExW(handle, None, buf, ctypes.sizeof(buf))
        kernel32.CloseHandle(handle)
        return buf.value.split("\\")[-1] if buf.value else ""
    except Exception:
        return ""
