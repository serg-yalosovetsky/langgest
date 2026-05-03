from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    vad_enabled: bool = True
    vad_threshold: float = 0.6
    wake_words_ru: list[str] = field(default_factory=lambda: ["компьютер", "ассистент"])
    wake_words_en: list[str] = field(default_factory=lambda: ["computer", "assistant"])


@dataclass
class ASRConfig:
    engine: str = "sherpa-onnx"
    model_path: str = "models/ru"
    model: str = "base.en"


@dataclass
class CameraConfig:
    device_index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30
    enabled: bool = True


@dataclass
class GestureConfig:
    enabled: bool = True
    confidence_threshold: float = 0.75
    min_stable_frames: int = 5
    cooldown_ms: int = 700
    safe_gestures_without_voice: list[str] = field(default_factory=lambda: [
        "media.play_pause", "media.next", "media.previous", "volume.up", "volume.down"
    ])


@dataclass
class SecurityConfig:
    dangerous_commands_require_confirmation: bool = True
    log_clipboard_content: bool = False
    log_audio: bool = False
    log_video: bool = False


@dataclass
class StorageConfig:
    db_path: str = "data/assistant.db"
    log_path: str = "data/events.jsonl"


@dataclass
class AppConfig:
    language_default: str = "ru"
    startup_enabled: bool = False
    debug_mode: bool = False


@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    asr_ru: ASRConfig = field(default_factory=ASRConfig)
    asr_en: ASRConfig = field(default_factory=lambda: ASRConfig(engine="faster-whisper", model="base.en"))
    camera: CameraConfig = field(default_factory=CameraConfig)
    gestures: GestureConfig = field(default_factory=GestureConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


def _from_dict(cls, data: dict[str, Any]):
    fields = {f.name for f in cls.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in fields}
    return cls(**filtered)


def load_config(path: str | Path = "config/app.yaml") -> Config:
    path = Path(path)
    if not path.exists():
        return Config()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    app_raw = raw.get("app", {})
    audio_raw = raw.get("audio", {})
    asr_raw = raw.get("asr", {})
    camera_raw = raw.get("camera", {})
    gestures_raw = raw.get("gestures", {})
    security_raw = raw.get("security", {})
    storage_raw = raw.get("storage", {})

    return Config(
        app=_from_dict(AppConfig, app_raw),
        audio=_from_dict(AudioConfig, audio_raw),
        asr_ru=_from_dict(ASRConfig, asr_raw.get("ru", {})),
        asr_en=_from_dict(ASRConfig, asr_raw.get("en", {})),
        camera=_from_dict(CameraConfig, camera_raw),
        gestures=_from_dict(GestureConfig, gestures_raw),
        security=_from_dict(SecurityConfig, security_raw),
        storage=_from_dict(StorageConfig, storage_raw),
    )
