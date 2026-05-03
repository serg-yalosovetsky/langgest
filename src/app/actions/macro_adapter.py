from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

import yaml

from app.nlu.intent import Intent

logger = logging.getLogger(__name__)


class MacroAdapter:
    def __init__(self, macros_path: str | Path = "config/macros.yaml") -> None:
        self._macros_path = Path(macros_path)
        self._macros: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self._macros_path.exists():
            logger.warning("Macros file not found: %s", self._macros_path)
            return
        with open(self._macros_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        for macro in raw.get("macros", []):
            self._macros[macro.get("id", macro.get("name", ""))] = macro
        logger.info("Loaded %d macros", len(self._macros))

    def execute_macro(self, intent: Intent) -> None:
        macro_name = intent.slots.get("macro_name") or intent.id.replace("macro.", "", 1)
        macro = self._macros.get(macro_name)
        if macro is None:
            logger.warning("Macro not found: %s", macro_name)
            return

        logger.info("Executing macro: %s", macro_name)
        for step in macro.get("steps", []):
            self._execute_step(step)

    def _execute_step(self, step: dict[str, Any]) -> None:
        action = step.get("action", "")
        try:
            if action == "hotkey":
                from app.actions.windows_adapter import send_hotkey
                send_hotkey(*step["keys"])

            elif action == "keypress":
                from app.actions.windows_adapter import send_keypress
                send_keypress(step["key"])

            elif action == "type_text":
                from app.actions.windows_adapter import type_text
                type_text(step["text"])

            elif action == "open_app":
                from app.actions.windows_adapter import open_app
                open_app(step["app"])

            elif action == "open_url":
                from app.actions.windows_adapter import open_url
                open_url(step["url"])

            elif action == "sleep":
                time.sleep(float(step.get("duration", 0.5)))

            else:
                logger.warning("Unknown macro action: %s", action)
        except Exception as e:
            logger.error("Macro step %s error: %s", action, e)
            raise
