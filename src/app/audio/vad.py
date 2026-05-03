from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


class VAD:
    """Voice Activity Detection. Uses silero-vad when available, falls back to energy threshold."""

    def __init__(self, threshold: float = 0.6, sample_rate: int = 16000) -> None:
        self._threshold = threshold
        self._sample_rate = sample_rate
        self._model = None
        self._available = False
        self._load()

    def _load(self) -> None:
        try:
            import torch  # type: ignore

            self._model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                onnx=False,
            )
            self._available = True
            logger.info("Silero VAD loaded")
        except Exception:
            logger.info("Silero VAD unavailable — using energy threshold fallback")

    def is_speech(self, audio_chunk: "np.ndarray") -> bool:
        """Return True if chunk contains speech."""
        if self._available and self._model is not None:
            return self._silero_check(audio_chunk)
        return self._energy_check(audio_chunk)

    def _silero_check(self, audio_chunk: "np.ndarray") -> bool:
        try:
            import torch  # type: ignore
            import numpy as np  # type: ignore

            tensor = torch.tensor(audio_chunk.astype("float32"))
            if tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)
            prob = self._model(tensor, self._sample_rate).item()
            return prob >= self._threshold
        except Exception as e:
            logger.debug("Silero VAD error: %s, falling back to energy", e)
            return self._energy_check(audio_chunk)

    def _energy_check(self, audio_chunk: "np.ndarray") -> bool:
        import numpy as np  # type: ignore

        rms = float(np.sqrt(np.mean(audio_chunk.astype("float64") ** 2)))
        return rms > 0.01
