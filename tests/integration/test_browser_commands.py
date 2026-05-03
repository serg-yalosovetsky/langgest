from __future__ import annotations

"""
Integration tests: voice text -> parser -> safety policy -> dispatcher.
No browser, no hardware needed.
"""

from pathlib import Path

import pytest

from app.nlu.command_parser import CommandParser
from app.policy.safety_policy import SafetyPolicy
from app.actions.dispatcher import CommandDispatcher
from app.storage.event_log import EventLog


@pytest.fixture
def browser_commands_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "browser_commands.yaml"
    p.write_text("""
commands:
  - id: browser.open_tab
    risk: safe
    patterns:
      ru:
        - "новая вкладка"
        - "открой новую вкладку"
      en:
        - "new tab"
        - "open new tab"
    action:
      type: hotkey
      keys: ["ctrl", "t"]

  - id: browser.close_tab
    risk: medium
    patterns:
      ru:
        - "закрой вкладку"
      en:
        - "close tab"
    action:
      type: hotkey
      keys: ["ctrl", "w"]

  - id: browser.back
    risk: safe
    patterns:
      ru:
        - "назад"
      en:
        - "back"
    action:
      type: hotkey
      keys: ["alt", "left"]

  - id: browser.refresh
    risk: safe
    patterns:
      ru:
        - "обнови"
      en:
        - "refresh"
    action:
      type: hotkey
      keys: ["ctrl", "r"]
""")
    return p


def test_open_tab_full_pipeline(browser_commands_yaml, tmp_path):
    parser = CommandParser(browser_commands_yaml)
    policy = SafetyPolicy()
    log = EventLog(tmp_path / "events.jsonl")
    dispatcher = CommandDispatcher(event_log=log)

    executed = []
    dispatcher.register("browser.open_tab", lambda i: executed.append(i.id))

    intent = parser.parse("новая вкладка", language="ru")
    assert intent is not None
    assert intent.id == "browser.open_tab"

    decision = policy.evaluate(intent)
    assert decision.allowed is True

    dispatcher.execute(intent)
    assert "browser.open_tab" in executed


def test_close_tab_high_confidence_allowed(browser_commands_yaml, tmp_path):
    parser = CommandParser(browser_commands_yaml)
    policy = SafetyPolicy()

    intent = parser.parse("закрой вкладку", language="ru")
    assert intent is not None

    # High confidence exact match
    intent.confidence = 0.95
    decision = policy.evaluate(intent)
    assert decision.allowed is True


def test_close_tab_low_confidence_blocked(browser_commands_yaml):
    parser = CommandParser(browser_commands_yaml)
    policy = SafetyPolicy()

    intent = parser.parse("закрой вкладку", language="ru")
    assert intent is not None

    intent.confidence = 0.60
    decision = policy.evaluate(intent)
    assert decision.allowed is False
    assert decision.requires_confirmation is True


def test_back_navigation(browser_commands_yaml, tmp_path):
    parser = CommandParser(browser_commands_yaml)
    policy = SafetyPolicy()
    log = EventLog(tmp_path / "events.jsonl")
    dispatcher = CommandDispatcher(event_log=log)

    executed = []
    dispatcher.register("browser.back", lambda i: executed.append(i.id))

    intent = parser.parse("назад", language="ru")
    assert intent is not None

    decision = policy.evaluate(intent)
    assert decision.allowed is True

    dispatcher.execute(intent)
    assert "browser.back" in executed


def test_english_new_tab(browser_commands_yaml, tmp_path):
    parser = CommandParser(browser_commands_yaml)
    policy = SafetyPolicy()

    intent = parser.parse("new tab", language="en")
    assert intent is not None
    assert intent.id == "browser.open_tab"

    decision = policy.evaluate(intent)
    assert decision.allowed is True


def test_refresh_page(browser_commands_yaml, tmp_path):
    parser = CommandParser(browser_commands_yaml)

    intent = parser.parse("обнови", language="ru")
    assert intent is not None
    assert intent.id == "browser.refresh"
