from __future__ import annotations

import logging

from app.audio.asr_base import ASREngine, ASRResult

logger = logging.getLogger(__name__)


class FasterWhisperASR(ASREngine):
    """English ASR using faster-whisper."""

    def __init__(self, model: str = "base.en") -> None:
        self._model_name = model
        self._model = None
        self._available = False
        self._load()

    def _load(self) -> None:
        try:
            from faster_whisper import WhisperModel  # type: ignore

            self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8")
            self._available = True
            logger.info("FasterWhisperASR loaded: %s", self._model_name)
        except ImportError:
            logger.warning("faster-whisper not installed — EN ASR unavailable")
        except Exception as e:
            logger.error("Failed to load FasterWhisperASR: %s", e)

    def transcribe(self, audio_data: "np.ndarray", sample_rate: int = 16000) -> ASRResult | None:
        if not self._available or self._model is None:
            return None
        try:
            import numpy as np  # type: ignore

            segments, info = self._model.transcribe(
                audio_data.astype(np.float32),
                language="en",
                beam_size=5,
            )
            text = " ".join(seg.text for seg in segments).strip()
            if not text:
                return None
            return ASRResult(text=text, confidence=0.9, language="en")
        except Exception as e:
            logger.error("FasterWhisperASR transcription error: %s", e)
            return None

    def is_available(self) -> bool:
        return self._available
