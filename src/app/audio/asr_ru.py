from __future__ import annotations

import logging
from pathlib import Path

from app.audio.asr_base import ASREngine, ASRResult

logger = logging.getLogger(__name__)


class SherpaOnnxASR(ASREngine):
    """Russian ASR using sherpa-onnx (offline transducer model)."""

    def __init__(self, model_path: str | Path = "models/ru") -> None:
        self._model_path = Path(model_path)
        self._recognizer = None
        self._available = False
        self._load()

    def _load(self) -> None:
        try:
            import sherpa_onnx  # type: ignore

            encoder = self._model_path / "encoder.onnx"
            decoder = self._model_path / "decoder.onnx"
            joiner = self._model_path / "joiner.onnx"
            tokens = self._model_path / "tokens.txt"

            if not all(p.exists() for p in [encoder, decoder, joiner, tokens]):
                logger.warning(
                    "sherpa-onnx RU model files not found in %s — RU ASR unavailable",
                    self._model_path,
                )
                return

            transducer = sherpa_onnx.OnlineTransducer(
                encoder=str(encoder),
                decoder=str(decoder),
                joiner=str(joiner),
            )
            self._recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                transducer=transducer,
                tokens=str(tokens),
                num_threads=2,
                sample_rate=16000,
            )
            self._available = True
            logger.info("SherpaOnnxASR loaded from %s", self._model_path)
        except ImportError:
            logger.warning("sherpa-onnx not installed — RU ASR unavailable")
        except Exception as e:
            logger.error("Failed to load SherpaOnnxASR: %s", e)

    def transcribe(self, audio_data: "np.ndarray", sample_rate: int = 16000) -> ASRResult | None:
        if not self._available or self._recognizer is None:
            return None
        try:
            import sherpa_onnx  # type: ignore
            import numpy as np  # type: ignore

            stream = self._recognizer.create_stream()
            stream.accept_waveform(sample_rate, audio_data.astype(np.float32))
            self._recognizer.decode_stream(stream)
            text = stream.result.text.strip()
            if not text:
                return None
            return ASRResult(text=text, confidence=0.9, language="ru")
        except Exception as e:
            logger.error("SherpaOnnxASR transcription error: %s", e)
            return None

    def is_available(self) -> bool:
        return self._available
