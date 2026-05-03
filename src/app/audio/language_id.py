from __future__ import annotations

import unicodedata


def detect_language(text: str) -> str:
    """Heuristic language detection: count Cyrillic vs Latin characters."""
    cyrillic = 0
    latin = 0
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("L"):
            name = unicodedata.name(ch, "")
            if "CYRILLIC" in name:
                cyrillic += 1
            elif "LATIN" in name:
                latin += 1
    return "ru" if cyrillic >= latin else "en"


def detect_wake_word(text: str, wake_words_ru: list[str], wake_words_en: list[str]) -> str | None:
    """Return detected language from wake word, or None if no wake word found."""
    lower = text.lower()
    for w in wake_words_ru:
        if lower.startswith(w):
            return "ru"
    for w in wake_words_en:
        if lower.startswith(w):
            return "en"
    return None
