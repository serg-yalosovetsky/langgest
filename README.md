# Voice & Gesture Desktop Assistant

Local Windows desktop agent — voice commands (RU/EN) + hand gesture control via webcam.

## Quick Start

```bash
pip install -e ".[dev]"
# Download models:
#   RU: place sherpa-onnx transducer files in models/ru/
#   EN: faster-whisper downloads automatically on first run
python -m app.main
```

## Requirements

- Windows 10/11 (for full feature set; Linux works for development/testing)
- Python 3.11+
- 720p+ webcam (gesture control)
- Microphone

## Testing (no hardware needed)

```bash
pytest tests/ -q
```

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

## Voice Commands (RU)

| Command | Action |
|---|---|
| компьютер, открой браузер | Open browser |
| новая вкладка | Ctrl+T |
| закрой вкладку | Ctrl+W |
| следующий трек | Next track |
| громче | Volume +5 |
| тише | Volume -5 |
| следующее окно | Alt+Tab |

## Gesture Commands

| Gesture | Action |
|---|---|
| Open palm | Play/Pause |
| Fist | Cancel/stop |
| Swipe left | Previous/back |
| Swipe right | Next/forward |
| Hand up | Volume up |
| Hand down | Volume down |
| Pinch | Click/select |

## Configuration

Edit `config/app.yaml` to change:
- Default language
- Wake words
- ASR engine paths
- Gesture thresholds
- Security settings

See `docs/command_reference.md` for the full command list.
