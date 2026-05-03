from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from app.nlu import normalizer, fuzzy_matcher
from app.nlu.intent import Intent, IntentSource

logger = logging.getLogger(__name__)


class CommandDefinition:
    def __init__(self, raw: dict[str, Any]) -> None:
        self.id: str = raw["id"]
        self.risk: str = raw.get("risk", "safe")
        self.patterns: dict[str, list[str]] = raw.get("patterns", {})
        self.slots: dict[str, Any] = raw.get("slots", {})
        self.action: dict[str, Any] = raw.get("action", {})

    def get_patterns(self, language: str) -> list[str]:
        return self.patterns.get(language, [])


def _slot_pattern(pattern: str) -> tuple[str, list[str]]:
    """Convert 'найди {query}' into a regex and list of slot names."""
    slot_names = re.findall(r"\{(\w+)\}", pattern)
    regex_str = re.escape(pattern)
    for name in slot_names:
        regex_str = regex_str.replace(re.escape(f"{{{name}}}"), r"(.+?)")
    regex_str = f"^{regex_str}$"
    return regex_str, slot_names


class CommandParser:
    def __init__(self, commands_path: str | Path = "config/commands.yaml") -> None:
        self._commands: list[CommandDefinition] = []
        self._load(Path(commands_path))

    def _load(self, path: Path) -> None:
        if not path.exists():
            logger.warning("Commands file not found: %s", path)
            return
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        for cmd_raw in raw.get("commands", []):
            self._commands.append(CommandDefinition(cmd_raw))
        logger.info("Loaded %d command definitions", len(self._commands))

    def parse(self, text: str, language: str = "ru") -> Intent | None:
        normalized = normalizer.normalize(text, language)
        if not normalized:
            return None

        # Phase 1: exact match
        for cmd in self._commands:
            for pattern in cmd.get_patterns(language):
                if "{" in pattern:
                    continue
                if normalizer.normalize(pattern, language) == normalized:
                    return Intent(
                        id=cmd.id,
                        source=IntentSource.VOICE,
                        confidence=1.0,
                        language=language,
                        text=normalized,
                    )

        # Phase 2: slot pattern match
        for cmd in self._commands:
            for pattern in cmd.get_patterns(language):
                if "{" not in pattern:
                    continue
                norm_pattern = normalizer.normalize(pattern, language)
                regex, slot_names = _slot_pattern(norm_pattern)
                m = re.match(regex, normalized)
                if m:
                    slots = dict(zip(slot_names, m.groups()))
                    return Intent(
                        id=cmd.id,
                        source=IntentSource.VOICE,
                        confidence=0.95,
                        language=language,
                        text=normalized,
                        slots=slots,
                    )

        # Phase 3: fuzzy match (no-slot patterns only)
        all_patterns: list[tuple[CommandDefinition, str]] = []
        for cmd in self._commands:
            for pattern in cmd.get_patterns(language):
                if "{" not in pattern:
                    all_patterns.append((cmd, normalizer.normalize(pattern, language)))

        best_score = 0.0
        best_cmd: CommandDefinition | None = None
        for cmd, norm_pattern in all_patterns:
            score = fuzzy_matcher.ratio(normalized, norm_pattern)
            if score > best_score:
                best_score = score
                best_cmd = cmd

        if best_cmd is not None and best_score >= 0.70:
            return Intent(
                id=best_cmd.id,
                source=IntentSource.VOICE,
                confidence=best_score,
                language=language,
                text=normalized,
            )

        return None
