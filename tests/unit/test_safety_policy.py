from __future__ import annotations

import pytest

from app.policy.safety_policy import SafetyPolicy
from app.nlu.intent import Intent, IntentSource, RiskLevel


def _intent(intent_id: str, confidence: float = 0.95) -> Intent:
    return Intent(id=intent_id, source=IntentSource.VOICE, confidence=confidence)


def test_volume_up_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("volume.up"))
    assert d.allowed is True
    assert d.risk_level == RiskLevel.SAFE


def test_media_play_pause_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("media.play_pause"))
    assert d.allowed is True
    assert d.risk_level == RiskLevel.SAFE


def test_media_next_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("media.next"))
    assert d.allowed is True


def test_browser_open_tab_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("browser.open_tab"))
    assert d.allowed is True
    assert d.risk_level == RiskLevel.SAFE


def test_browser_close_tab_high_confidence():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("browser.close_tab", confidence=0.95))
    assert d.allowed is True
    assert d.risk_level == RiskLevel.MEDIUM


def test_browser_close_tab_low_confidence():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("browser.close_tab", confidence=0.60))
    assert d.allowed is False
    assert d.requires_confirmation is True


def test_shell_execute_dangerous():
    policy = SafetyPolicy(require_confirmation_for_dangerous=True)
    d = policy.evaluate(_intent("shell.execute"))
    assert d.allowed is False
    assert d.requires_confirmation is True
    assert d.risk_level == RiskLevel.DANGEROUS


def test_shell_execute_no_confirmation_required():
    policy = SafetyPolicy(require_confirmation_for_dangerous=False)
    d = policy.evaluate(_intent("shell.execute"))
    assert d.allowed is True


def test_system_format_forbidden():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("system.format_disk"))
    assert d.allowed is False
    assert d.requires_confirmation is False
    assert d.risk_level == RiskLevel.FORBIDDEN


def test_system_destroy_forbidden():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("system.destroy"))
    assert d.allowed is False
    assert d.risk_level == RiskLevel.FORBIDDEN


def test_shell_clear_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("shell.clear"))
    assert d.allowed is True


def test_shell_stop_safe():
    policy = SafetyPolicy()
    d = policy.evaluate(_intent("shell.stop_process"))
    assert d.allowed is True
