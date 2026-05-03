from __future__ import annotations

import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)


class TrayIcon:
    """System tray icon. Uses PySide6 when available; falls back to console mode."""

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_toggle_voice: Callable[[bool], None] | None = None,
        on_toggle_gesture: Callable[[bool], None] | None = None,
    ) -> None:
        self._on_quit = on_quit
        self._on_toggle_voice = on_toggle_voice
        self._on_toggle_gesture = on_toggle_gesture
        self._voice_enabled = True
        self._gesture_enabled = True
        self._app = None
        self._tray = None

    def start(self) -> None:
        try:
            self._start_pyside()
        except ImportError:
            logger.info("PySide6 not available — tray icon disabled")
        except Exception as e:
            logger.error("Tray icon error: %s", e)

    def _start_pyside(self) -> None:
        from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu  # type: ignore
        from PySide6.QtGui import QIcon, QAction  # type: ignore
        from PySide6.QtCore import Qt  # type: ignore
        import sys

        self._app = QApplication.instance() or QApplication(sys.argv)
        icon = QIcon.fromTheme("audio-input-microphone")
        self._tray = QSystemTrayIcon(icon)
        self._tray.setToolTip("Voice & Gesture Assistant")

        menu = QMenu()

        voice_action = QAction("Voice: ON", checkable=True)
        voice_action.setChecked(True)
        voice_action.triggered.connect(self._toggle_voice)
        menu.addAction(voice_action)

        gesture_action = QAction("Gesture: ON", checkable=True)
        gesture_action.setChecked(True)
        gesture_action.triggered.connect(self._toggle_gesture)
        menu.addAction(gesture_action)

        menu.addSeparator()
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.show()
        logger.info("Tray icon started")

    def _toggle_voice(self, checked: bool) -> None:
        self._voice_enabled = checked
        if self._on_toggle_voice:
            self._on_toggle_voice(checked)

    def _toggle_gesture(self, checked: bool) -> None:
        self._gesture_enabled = checked
        if self._on_toggle_gesture:
            self._on_toggle_gesture(checked)

    def _quit(self) -> None:
        self._on_quit()

    def show_notification(self, title: str, message: str) -> None:
        if self._tray:
            try:
                from PySide6.QtWidgets import QSystemTrayIcon  # type: ignore

                self._tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
            except Exception:
                pass
        else:
            logger.info("[Notification] %s: %s", title, message)
