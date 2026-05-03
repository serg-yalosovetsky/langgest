from __future__ import annotations

import pytest
from pathlib import Path

from app.actions.macro_adapter import MacroAdapter
from app.nlu.intent import Intent, IntentSource


@pytest.fixture
def macros_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "macros.yaml"
    p.write_text("""
macros:
  - id: test.macro
    name: "test_macro"
    steps:
      - action: sleep
        duration: 0.01
      - action: sleep
        duration: 0.01
  - id: multi.step
    name: "multi_step"
    steps:
      - action: sleep
        duration: 0.01
      - action: sleep
        duration: 0.01
      - action: sleep
        duration: 0.01
""")
    return p


def _intent(macro_id: str, macro_name: str) -> Intent:
    return Intent(
        id=f"macro.{macro_id}",
        source=IntentSource.VOICE,
        slots={"macro_name": macro_id},
    )


def test_macro_executes_without_error(macros_yaml):
    adapter = MacroAdapter(macros_path=macros_yaml)
    intent = _intent("test.macro", "test_macro")
    adapter.execute_macro(intent)  # must not raise


def test_multi_step_macro(macros_yaml):
    adapter = MacroAdapter(macros_path=macros_yaml)
    intent = _intent("multi.step", "multi_step")
    adapter.execute_macro(intent)


def test_missing_macro_logs_warning(macros_yaml, caplog):
    import logging
    adapter = MacroAdapter(macros_path=macros_yaml)
    intent = _intent("nonexistent", "nonexistent")
    with caplog.at_level(logging.WARNING):
        adapter.execute_macro(intent)
    assert "not found" in caplog.text.lower()


def test_empty_macros_file(tmp_path):
    p = tmp_path / "empty_macros.yaml"
    p.write_text("macros: []\n")
    adapter = MacroAdapter(macros_path=p)
    intent = _intent("anything", "anything")
    adapter.execute_macro(intent)  # should not raise, just warn


def test_macro_file_missing(tmp_path):
    adapter = MacroAdapter(macros_path=tmp_path / "nonexistent.yaml")
    intent = _intent("test.macro", "test_macro")
    adapter.execute_macro(intent)  # should not raise
