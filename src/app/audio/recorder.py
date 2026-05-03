from __future__ import annotations

import logging
import threading
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

from app.audio.asr_base import ASREngine
from app.audio.vad import VAD
from app.audio.language_id import detect_language, detect_wake_word
from app.event_bus import EventBus, Event
from app.storage.config_loader import AudioConfig

logger = logging.getLogger(__name__)

CHUNK_DURATION_MS = 100
SPEECH_FRAMES_NEEDED = 3
SILENCE_FRAMES_TO_STOP = 10


class AudioRecorder:
    """Records audio from microphone, detects speech, dispatches voice.text events."""

    def __init__(
        self,
        config: AudioConfig,
        bus: EventBus,
        asr_ru: ASREngine,
        asr_en: ASREngine,
    ) -> None:
        self._config = config
        self._bus = bus
        self._asr_ru = asr_ru
        self._asr_en = asr_en
        self._vad = VAD(threshold=config.vad_threshold, sample_rate=config.sample_rate)
        self._thread: threading.Thread | None = None
        self._running = False
        self._injected: list["np.ndarray"] = []

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="AudioRecorder")
        self._thread.start()
        logger.info("AudioRecorder started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("AudioRecorder stopped")

    def inject_audio(self, audio_data: "np.ndarray") -> None:
        """Bypass microphone and process audio_data directly (for testing)."""
        self._injected.append(audio_data)

    def _run(self) -> None:
        # Try real microphone; if unavailable, drain injected queue
        try:
            import sounddevice as sd  # type: ignore
            import numpy as np

            sr = self._config.sample_rate
            chunk_size = int(sr * CHUNK_DURATION_MS / 1000)
            speech_buffer: list[np.ndarray] = []
            speech_frames = 0
            silence_frames = 0
            recording = False

            def callback(indata: np.ndarray, frames: int, time_info, status) -> None:
                nonlocal speech_frames, silence_frames, recording, speech_buffer
                chunk = indata[:, 0].copy()
                if self._vad.is_speech(chunk):
                    speech_frames += 1
                    silence_frames = 0
                    if speech_frames >= SPEECH_FRAMES_NEEDED:
                        recording = True
                    if recording:
                        speech_buffer.append(chunk)
                else:
                    silence_frames += 1
                    if recording:
                        speech_buffer.append(chunk)
                    if recording and silence_frames >= SILENCE_FRAMES_TO_STOP:
                        audio = np.concatenate(speech_buffer)
                        self._transcribe_and_post(audio)
                        speech_buffer = []
                        speech_frames = 0
                        silence_frames = 0
                        recording = False

            with sd.InputStream(
                samplerate=sr,
                channels=self._config.channels,
                blocksize=chunk_size,
                dtype="float32",
                callback=callback,
            ):
                while self._running:
                    sd.sleep(50)
        except ImportError:
            logger.info("sounddevice not available — AudioRecorder in injection-only mode")
            import time

            while self._running:
                if self._injected:
                    data = self._injected.pop(0)
                    self._transcribe_and_post(data)
                else:
                    time.sleep(0.05)

    def _transcribe_and_post(self, audio: "np.ndarray") -> None:
        cfg = self._config
        language = cfg.wake_words_ru[0][:1] and "ru" or "en"

        # Try to detect language from wake word using energy-based text preview
        # (full approach: run a tiny language classifier on audio; here we default to configured)
        lang = self._config.__dict__.get("language_default", "ru")

        asr = self._asr_ru if lang == "ru" else self._asr_en
        if not asr.is_available():
            asr = self._asr_en if lang == "ru" else self._asr_ru
        if not asr.is_available():
            return

        result = asr.transcribe(audio, self._config.sample_rate)
        if result is None or not result.text.strip():
            return

        # Detect language from recognized text
        detected_lang = detect_wake_word(
            result.text,
            cfg.wake_words_ru,
            cfg.wake_words_en,
        ) or detect_language(result.text)

        self._bus.post(Event(
            type="voice.text",
            payload={"text": result.text, "language": detected_lang, "confidence": result.confidence},
        ))
        logger.debug("ASR result [%s]: %s", detected_lang, result.text)
