from __future__ import annotations

import pytest
from pathlib import Path

from app.actions.shell_adapter import ShellAdapter
from app.nlu.intent import Intent, IntentSource


@pytest.fixture
def policy_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "shell_policy.yaml"
    p.write_text("""
shell_policy:
  auto_execute_allowed:
    - "echo *"
    - "dir"
    - "ls"
    - "cls"
    - "pwd"
    - "git status"

  require_confirmation_patterns:
    - "git push"
    - "docker compose down"
    - "rm "
    - "del "
    - "shutdown"

  forbidden_patterns:
    - "rm -rf /"
    - "del /f /q C:\\\\"
    - "format c:"
""")
    return p


def _cmd_intent(command: str) -> Intent:
    return Intent(
        id="shell.execute",
        source=IntentSource.VOICE,
        slots={"command": command},
    )


def test_allowed_command_executes(policy_yaml):
    adapter = ShellAdapter(policy_path=policy_yaml)
    # "echo hello" matches "echo *" — should not raise PermissionError
    # (actual subprocess call is made; we just verify no policy block)
    intent = _cmd_intent("echo hello")
    adapter.execute(intent)  # no PermissionError


def test_ls_allowed(policy_yaml):
    adapter = ShellAdapter(policy_path=policy_yaml)
    intent = _cmd_intent("ls")
    adapter.execute(intent)


def test_git_push_blocked(policy_yaml):
    adapter = ShellAdapter(policy_path=policy_yaml)
    intent = _cmd_intent("git push origin main")
    with pytest.raises(PermissionError):
        adapter.execute(intent)


def test_rm_rf_blocked(policy_yaml):
    adapter = ShellAdapter(policy_path=policy_yaml)
    intent = _cmd_intent("rm -rf /tmp/test")
    with pytest.raises(PermissionError):
        adapter.execute(intent)


def test_forbidden_pattern_blocked(policy_yaml):
    adapter = ShellAdapter(policy_path=policy_yaml)
    intent = _cmd_intent("rm -rf /")
    with pytest.raises(PermissionError):
        adapter.execute(intent)


def test_empty_command_does_nothing(policy_yaml, caplog):
    import logging
    adapter = ShellAdapter(policy_path=policy_yaml)
    intent = Intent(id="shell.execute", source=IntentSource.VOICE, slots={})
    with caplog.at_level(logging.WARNING):
        adapter.execute(intent)
    assert "empty command" in caplog.text.lower()


def test_missing_policy_file(tmp_path):
    adapter = ShellAdapter(policy_path=tmp_path / "nonexistent.yaml")
    intent = _cmd_intent("git push")
    # With no policy loaded, _allowed is empty so any non-empty command is blocked
    with pytest.raises(PermissionError):
        adapter.execute(intent)
