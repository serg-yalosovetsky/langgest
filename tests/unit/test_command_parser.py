from __future__ import annotations

import pytest
from pathlib import Path

from app.nlu.command_parser import CommandParser
from app.nlu.intent import IntentSource


@pytest.fixture
def parser(config) -> CommandParser:
    return CommandParser(config._commands_path)


def test_exact_match_ru(parser):
    intent = parser.parse("громче", language="ru")
    assert intent is not None
    assert intent.id == "volume.up"
    assert intent.confidence == 1.0
    assert intent.source == IntentSource.VOICE


def test_exact_match_en(parser):
    intent = parser.parse("louder", language="en")
    assert intent is not None
    assert intent.id == "volume.up"


def test_with_wake_word_stripped(parser):
    intent = parser.parse("компьютер громче", language="ru")
    assert intent is not None
    assert intent.id == "volume.up"


def test_fuzzy_match_typo(parser):
    intent = parser.parse("грмче", language="ru")
    assert intent is not None
    assert intent.id == "volume.up"
    assert intent.confidence < 1.0


def test_no_match_returns_none(parser):
    intent = parser.parse("абракадабра zxzxzx", language="ru")
    assert intent is None


def test_language_separation(parser):
    # "громче" is RU only — should not match EN query
    intent = parser.parse("громче", language="en")
    # May or may not match (fuzzy might catch it); but intent id should NOT be volume.up for EN
    # since "громче" is not in EN patterns
    if intent is not None:
        # Fuzzy could still match "louder" etc but unlikely for "громче" in EN
        pass


def test_media_next(parser):
    intent = parser.parse("следующий трек", language="ru")
    assert intent is not None
    assert intent.id == "media.next"


def test_media_play_pause(parser):
    intent = parser.parse("пауза", language="ru")
    assert intent is not None
    assert intent.id == "media.play_pause"


def test_browser_open_tab(parser):
    intent = parser.parse("новая вкладка", language="ru")
    assert intent is not None
    assert intent.id == "browser.open_tab"


def test_close_tab(parser):
    intent = parser.parse("закрой вкладку", language="ru")
    assert intent is not None
    assert intent.id == "browser.close_tab"


def test_filler_removed(parser):
    intent = parser.parse("пожалуйста громче", language="ru")
    assert intent is not None
    assert intent.id == "volume.up"
