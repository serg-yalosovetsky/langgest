from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from app.context.active_window import WindowInfo

logger = logging.getLogger(__name__)

BUILTIN_PROFILES = {
    "browser": {
        "process_names": ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"],
    },
    "terminal": {
        "process_names": ["WindowsTerminal.exe", "cmd.exe", "powershell.exe", "wt.exe", "bash.exe"],
    },
    "editor": {
        "process_names": ["Code.exe", "idea64.exe", "pycharm64.exe", "notepad++.exe", "vim.exe"],
    },
    "media": {
        "process_names": ["Spotify.exe", "vlc.exe", "wmplayer.exe", "MusicBee.exe"],
    },
}


class AppProfiles:
    """Maps active window to a named profile for context-aware command handling."""

    def __init__(self, profiles_path: str | Path | None = None) -> None:
        self._profiles: dict[str, dict[str, Any]] = dict(BUILTIN_PROFILES)
        if profiles_path:
            self._load(Path(profiles_path))

    def _load(self, path: Path) -> None:
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        for name, profile in raw.get("profiles", {}).items():
            self._profiles[name] = profile
        logger.info("Loaded %d app profiles", len(self._profiles))

    def detect_profile(self, window: WindowInfo) -> str:
        """Return the profile name for the given window, or 'default'."""
        proc_lower = window.process_name.lower()
        for profile_name, profile in self._profiles.items():
            for proc in profile.get("process_names", []):
                if proc.lower() == proc_lower:
                    return profile_name
        return "default"
