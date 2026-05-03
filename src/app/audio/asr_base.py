from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ASRResult:
    text: str
    confidence: float = 1.0
    language: str = "ru"


class ASREngine(ABC):
    """Abstract base for ASR engines."""

    @abstractmethod
    def transcribe(self, audio_data: "np.ndarray", sample_rate: int = 16000) -> ASRResult | None:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...


class MockASREngine(ASREngine):
    """Returns a fixed response — used in tests and --no-hardware mode."""

    def __init__(self, response: str = "", confidence: float = 1.0, language: str = "ru") -> None:
        self._response = response
        self._confidence = confidence
        self._language = language

    def transcribe(self, audio_data: "np.ndarray", sample_rate: int = 16000) -> ASRResult | None:
        if not self._response:
            return None
        return ASRResult(text=self._response, confidence=self._confidence, language=self._language)

    def is_available(self) -> bool:
        return True
