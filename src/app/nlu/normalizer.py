from __future__ import annotations

import re
import unicodedata


_WAKE_WORDS_RU = frozenset(["компьютер", "ассистент"])
_WAKE_WORDS_EN = frozenset(["computer", "assistant"])
_FILLER_RU = frozenset(["пожалуйста", "можешь", "ну", "вот", "там", "да", "же"])
_FILLER_EN = frozenset(["please", "can you", "could you", "hey", "just"])


def normalize(text: str, language: str = "ru") -> str:
    """Normalize ASR output: lowercase, strip punctuation, remove wake words and fillers."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w\sЀ-ӿ-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()
    wake = _WAKE_WORDS_RU if language == "ru" else _WAKE_WORDS_EN
    fillers = _FILLER_RU if language == "ru" else _FILLER_EN

    # Remove leading wake word only
    if words and words[0] in wake:
        words = words[1:]

    # Remove standalone fillers anywhere
    words = [w for w in words if w not in fillers]

    return " ".join(words).strip()
