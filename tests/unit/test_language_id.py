from __future__ import annotations

from app.audio.language_id import detect_language, detect_wake_word


def test_russian_text():
    assert detect_language("открой браузер") == "ru"


def test_english_text():
    assert detect_language("open the browser please") == "en"


def test_mixed_text_cyrillic_majority():
    assert detect_language("громче volume") == "ru"


def test_mixed_text_latin_majority():
    assert detect_language("play пауза pause") == "en"


def test_empty_string():
    result = detect_language("")
    assert result in ("ru", "en")


def test_wake_word_ru():
    lang = detect_wake_word(
        "компьютер открой браузер",
        wake_words_ru=["компьютер", "ассистент"],
        wake_words_en=["computer", "assistant"],
    )
    assert lang == "ru"


def test_wake_word_en():
    lang = detect_wake_word(
        "computer open browser",
        wake_words_ru=["компьютер", "ассистент"],
        wake_words_en=["computer", "assistant"],
    )
    assert lang == "en"


def test_no_wake_word():
    lang = detect_wake_word(
        "громче",
        wake_words_ru=["компьютер", "ассистент"],
        wake_words_en=["computer", "assistant"],
    )
    assert lang is None
