from __future__ import annotations

import logging
from typing import Callable

from app.nlu.intent import Intent
from app.storage.event_log import EventLog

logger = logging.getLogger(__name__)

ActionHandler = Callable[[Intent], None]


class CommandDispatcher:
    """Routes intents to registered action handlers and logs results."""

    def __init__(self, event_log: EventLog | None = None) -> None:
        self._log = event_log
        self._handlers: dict[str, ActionHandler] = {}
        self._register_defaults()

    def register(self, intent_id: str, handler: ActionHandler) -> None:
        self._handlers[intent_id] = handler

    def execute(self, intent: Intent, active_app: str = "") -> bool:
        handler = self._handlers.get(intent.id)
        if handler is None:
            handler = self._route_by_prefix(intent.id)
        if handler is None:
            logger.warning("No handler for intent: %s", intent.id)
            return False

        try:
            handler(intent)
            if self._log:
                self._log.log_intent(intent, active_app=active_app, result="success")
            return True
        except Exception as e:
            logger.error("Handler error for %s: %s", intent.id, e)
            if self._log:
                self._log.log_intent(intent, active_app=active_app, result="error", error=str(e))
            return False

    def _route_by_prefix(self, intent_id: str) -> ActionHandler | None:
        # Match longest registered prefix
        best: ActionHandler | None = None
        best_len = 0
        for registered_id, handler in self._handlers.items():
            if intent_id.startswith(registered_id) and len(registered_id) > best_len:
                best = handler
                best_len = len(registered_id)
        return best

    def _register_defaults(self) -> None:
        from app.actions import (
            windows_adapter,
            volume_adapter,
            media_adapter,
            clipboard_adapter,
            browser_adapter,
        )

        # Media
        self.register("media.play_pause", lambda i: media_adapter.play_pause())
        self.register("media.next", lambda i: media_adapter.next_track())
        self.register("media.previous", lambda i: media_adapter.previous_track())

        # Volume
        self.register("volume.up", lambda i: volume_adapter.change_volume(5))
        self.register("volume.down", lambda i: volume_adapter.change_volume(-5))
        self.register("volume.mute", lambda i: volume_adapter.set_mute(True))
        self.register("volume.unmute", lambda i: volume_adapter.set_mute(False))
        self.register("volume.set", lambda i: volume_adapter.set_volume(
            int(i.slots.get("level", 50)) / 100.0
        ))

        # Browser
        self.register("browser.open", lambda i: windows_adapter.open_app(
            i.slots.get("app", "chrome")
        ))
        self.register("browser.open_tab", lambda i: windows_adapter.send_hotkey("ctrl", "t"))
        self.register("browser.close_tab", lambda i: windows_adapter.send_hotkey("ctrl", "w"))
        self.register("browser.next_tab", lambda i: windows_adapter.send_hotkey("ctrl", "tab"))
        self.register("browser.previous_tab", lambda i: windows_adapter.send_hotkey("ctrl", "shift", "tab"))
        self.register("browser.back", lambda i: windows_adapter.send_hotkey("alt", "left"))
        self.register("browser.forward", lambda i: windows_adapter.send_hotkey("alt", "right"))
        self.register("browser.refresh", lambda i: windows_adapter.send_hotkey("ctrl", "r"))
        self.register("browser.search", lambda i: browser_adapter.search(i.slots.get("query", "")))

        # Window
        self.register("window.next", lambda i: windows_adapter.send_hotkey("alt", "tab"))
        self.register("window.previous", lambda i: windows_adapter.send_hotkey("alt", "shift", "tab"))
        self.register("window.show_all", lambda i: windows_adapter.send_hotkey("win", "tab"))
        self.register("window.go_to_browser", lambda i: windows_adapter.activate_window_by_process(
            ["chrome.exe", "msedge.exe", "firefox.exe"]
        ))
        self.register("window.go_to_terminal", lambda i: windows_adapter.activate_window_by_process(
            ["WindowsTerminal.exe", "cmd.exe", "powershell.exe"]
        ))
        self.register("window.go_to_editor", lambda i: windows_adapter.activate_window_by_process(
            ["Code.exe", "idea64.exe", "pycharm64.exe"]
        ))

        # Clipboard
        self.register("clipboard.copy", lambda i: clipboard_adapter.copy())
        self.register("clipboard.cut", lambda i: clipboard_adapter.cut())
        self.register("clipboard.paste", lambda i: clipboard_adapter.paste())
        self.register("clipboard.clear", lambda i: clipboard_adapter.clear())
        self.register("clipboard.read", lambda i: clipboard_adapter.read())

        # Shell
        self.register("shell.clear", lambda i: windows_adapter.type_text("cls\n"))
        self.register("shell.stop_process", lambda i: windows_adapter.send_hotkey("ctrl", "c"))
        self.register("shell.last_command", lambda i: windows_adapter.send_keypress("up"))

        # Gesture actions
        self.register("action.cancel", lambda i: None)
        self.register("action.click", lambda i: None)
        self.register("action.scroll_mode", lambda i: None)
