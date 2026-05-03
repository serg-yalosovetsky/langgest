from __future__ import annotations

import fnmatch
import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml

from app.nlu.intent import Intent

logger = logging.getLogger(__name__)


class ShellAdapter:
    def __init__(self, policy_path: str | Path = "config/shell_policy.yaml") -> None:
        self._policy_path = Path(policy_path)
        self._allowed: list[str] = []
        self._require_confirm: list[str] = []
        self._forbidden: list[str] = []
        self._load()

    def _load(self) -> None:
        if not self._policy_path.exists():
            logger.warning("Shell policy file not found: %s", self._policy_path)
            return
        with open(self._policy_path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        policy = raw.get("shell_policy", {})
        self._allowed = policy.get("auto_execute_allowed", [])
        self._require_confirm = policy.get("require_confirmation_patterns", [])
        self._forbidden = policy.get("forbidden_patterns", [])

    def execute(self, intent: Intent) -> None:
        command = intent.slots.get("command", "")
        if not command:
            logger.warning("shell.execute called with empty command")
            return

        if self._is_forbidden(command):
            raise PermissionError(f"Command is explicitly forbidden: {command!r}")

        if not self._is_allowed(command):
            raise PermissionError(f"Command blocked by shell policy (requires confirmation): {command!r}")

        try:
            subprocess.Popen(command, shell=True)
            logger.info("Shell execute: %s", command)
        except Exception as e:
            logger.error("Shell execute error: %s", e)
            raise

    def insert(self, command: str) -> None:
        """Type command into active terminal without executing it."""
        from app.actions.windows_adapter import type_text
        type_text(command)

    def _is_forbidden(self, command: str) -> bool:
        cmd_lower = command.lower()
        return any(pattern.lower() in cmd_lower for pattern in self._forbidden)

    def _is_allowed(self, command: str) -> bool:
        cmd_lower = command.lower()
        return any(fnmatch.fnmatch(cmd_lower, pattern.lower()) for pattern in self._allowed)
