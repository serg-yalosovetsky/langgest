from __future__ import annotations

import pytest
from pathlib import Path

from app.audio.asr_base import MockASREngine
from app.storage.event_log import EventLog
from app.storage.config_loader import Config


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Return a Config with temporary paths pointing to a minimal commands.yaml."""
    commands_yaml = tmp_path / "commands.yaml"
    commands_yaml.write_text("""
commands:
  - id: volume.up
    risk: safe
    patterns:
      ru:
        - "громче"
        - "увеличь громкость"
      en:
        - "louder"
        - "volume up"
    action:
      type: volume
      delta: 5

  - id: volume.down
    risk: safe
    patterns:
      ru:
        - "тише"
      en:
        - "quieter"
        - "volume down"
    action:
      type: volume
      delta: -5

  - id: media.play_pause
    risk: safe
    patterns:
      ru:
        - "пауза"
        - "продолжить"
        - "поставь на паузу"
      en:
        - "pause"
        - "play"
    action:
      type: hotkey
      keys: ["playpause"]

  - id: media.next
    risk: safe
    patterns:
      ru:
        - "следующий трек"
        - "следующая песня"
        - "дальше"
      en:
        - "next track"
        - "next song"
    action:
      type: hotkey
      keys: ["nexttrack"]

  - id: media.previous
    risk: safe
    patterns:
      ru:
        - "предыдущий трек"
        - "предыдущая песня"
      en:
        - "previous track"
        - "previous song"
    action:
      type: hotkey
      keys: ["prevtrack"]

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
""")

    cfg = Config()
    cfg._commands_path = commands_yaml
    # Attach commands_path so tests can reference it
    object.__setattr__(cfg, "_commands_path_override", commands_yaml)
    return cfg


@pytest.fixture
def commands_path(config) -> Path:
    return config._commands_path


@pytest.fixture
def event_log(tmp_path: Path) -> EventLog:
    return EventLog(log_path=tmp_path / "test_events.jsonl", log_clipboard_content=False)


@pytest.fixture
def mock_asr_ru() -> MockASREngine:
    return MockASREngine(response="", language="ru")


@pytest.fixture
def mock_asr_en() -> MockASREngine:
    return MockASREngine(response="", language="en")
