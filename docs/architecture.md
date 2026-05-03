# Architecture

## Pipeline

```
Input signal
  -> recognition (ASR / gesture)
  -> intent extraction
  -> confidence scoring
  -> context detection
  -> safety policy
  -> command dispatch
  -> action execution
  -> logging
```

## Components

### Audio pipeline
`Microphone -> VAD -> Language detection -> ASR engine -> EventBus(voice.text)`

- **VAD** (`audio/vad.py`): Silero VAD with energy fallback. Segments continuous audio into speech chunks.
- **Language detection** (`audio/language_id.py`): Wake-word heuristic + Cyrillic/Latin character ratio.
- **ASR RU** (`audio/asr_ru.py`): `sherpa-onnx` transducer model (offline).
- **ASR EN** (`audio/asr_en.py`): `faster-whisper` (downloads on first use).

### Vision pipeline
`Camera -> MediaPipe Hands -> Landmark extraction -> Gesture classifier -> Temporal smoother -> EventBus(gesture.detected)`

- **MPHandsDetector** (`vision/mediapipe_hands.py`): MediaPipe Hands wrapper, returns 21-point landmarks.
- **GestureClassifier** (`vision/gesture_classifier.py`): Heuristic classifier (open palm, fist, pinch, two fingers).
- **GestureSmoothing** (`vision/gesture_smoothing.py`): Anti-false-positive filter (stable frames + cooldown).

### NLU
`voice.text event -> normalize -> exact/fuzzy match -> Intent`

- **Normalizer** (`nlu/normalizer.py`): Lowercase, strip wake words, remove fillers.
- **CommandParser** (`nlu/command_parser.py`): Exact match → slot pattern match → fuzzy match (difflib).
- **Intent** (`nlu/intent.py`): Core data class. `id`, `source`, `confidence`, `language`, `slots`.

### Fusion engine (`fusion/fusion_engine.py`)
Combines voice and gesture intents within a 1.5-second window.

| Situation | Result |
|---|---|
| Voice alone | Passed through |
| Safe gesture alone | Passed through |
| Unsafe gesture alone | Dropped |
| Voice + gesture (fusion rule matches) | Fused intent |
| Voice + gesture (no rule) | Voice wins, gesture dropped |

### Safety policy (`policy/safety_policy.py`)

| Risk level | Examples | Behavior |
|---|---|---|
| SAFE | volume, media, browser tabs | Execute immediately |
| MEDIUM | close tab, clipboard, shell insert | Execute if confidence ≥ 0.80 |
| DANGEROUS | shell.execute | Require confirmation |
| FORBIDDEN | system.format, system.destroy | Block permanently |

### Command dispatcher (`actions/dispatcher.py`)
Routes `Intent.id` to registered `ActionHandler`. Falls back to prefix matching.

### Action adapters
| Adapter | File | Notes |
|---|---|---|
| Windows | `windows_adapter.py` | pyautogui hotkeys, open_app, activate_window |
| Volume | `volume_adapter.py` | pycaw; gracefully degrades on non-Windows |
| Media | `media_adapter.py` | Media key keypresses |
| Clipboard | `clipboard_adapter.py` | pyperclip; never logs raw content |
| Browser | `browser_adapter.py` | search via Ctrl+L |
| Shell | `shell_adapter.py` | Policy-gated subprocess |
| Macro | `macro_adapter.py` | YAML step executor |

### Storage
- **EventLog** (`storage/event_log.py`): JSONL, redacts clipboard/audio/video.
- **SQLiteStore** (`storage/sqlite_store.py`): Thread-safe events, macros, key-value.
- **ConfigLoader** (`storage/config_loader.py`): YAML → typed dataclasses.

### Context
- **ActiveWindow** (`context/active_window.py`): Win32 API to get foreground window and process name.
- **AppProfiles** (`context/app_profiles.py`): Maps process names to profiles (browser, terminal, editor, media).

### UI
- **TrayIcon** (`ui/tray.py`): PySide6 system tray, voice/gesture toggles, notifications.
- **DebugOverlay** (`ui/debug_overlay.py`): Ring buffer of recent intent events for debug display.
