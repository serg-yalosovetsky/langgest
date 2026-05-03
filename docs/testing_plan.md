# Testing Plan

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

No microphone, camera, or Windows installation required.

## Unit tests (`tests/unit/`)

| File | What it tests |
|---|---|
| `test_command_parser.py` | Phrase → intent; exact, fuzzy, slot, wake-word stripping, filler removal |
| `test_language_id.py` | Character-ratio language detection; wake-word detection |
| `test_safety_policy.py` | Risk classification; SAFE/MEDIUM/DANGEROUS/FORBIDDEN decisions |
| `test_macro_engine.py` | Macro loading, step execution, missing macro warning |
| `test_gesture_classifier.py` | Landmark-based classification without camera or MediaPipe |
| `test_gesture_smoothing.py` | Stable-frame filter, cooldown, low-confidence blocking |
| `test_fusion_engine.py` | Voice-only, gesture-only, fused, conflict resolution |

## Integration tests (`tests/integration/`)

| File | What it tests |
|---|---|
| `test_browser_commands.py` | Full pipeline: voice text → parser → policy → dispatcher |
| `test_shell_policy.py` | Shell adapter allowlist/denylist/forbidden enforcement |

## Golden test data (`tests/golden/`)

| File | Contents |
|---|---|
| `voice_commands.yaml` | 14 text → expected intent mappings (RU + EN) |
| `gestures.yaml` | 8 gesture name → expected intent mappings |

### Running golden tests manually

```python
import yaml
from app.nlu.command_parser import CommandParser

parser = CommandParser("config/commands.yaml")
cases = yaml.safe_load(open("tests/golden/voice_commands.yaml"))["cases"]
for case in cases:
    intent = parser.parse(case["text"], case["language"])
    assert intent is not None, f"No intent for: {case['text']!r}"
    assert intent.id == case["expected_intent"], f"Got {intent.id}, expected {case['expected_intent']}"
    assert intent.confidence >= case["min_confidence"]
```

## POC success criteria

| Metric | Target |
|---|---|
| Voice command accuracy | >85% on known commands |
| Gesture precision | >80% in good lighting |
| False positive rate | <1 unwanted action / 10 min |
| Simple command latency | <700 ms |
| System crash rate | 0 during 30 min manual session |

## Manual test scenarios

### Browser scenario
```
1. Say: "компьютер, открой браузер"
2. Say: "новая вкладка"
3. Say: "найди weather Kyiv"
4. Gesture: swipe left
5. Expected: browser opens, new tab, search, back navigation
```

### Media scenario
```
1. Start music player
2. Say: "пауза"         → play/pause
3. Gesture: open palm   → play/pause
4. Say: "следующий трек" → next track
5. Gesture: hand up     → volume +5
```

### Terminal safety scenario
```
1. Focus terminal
2. Say: "очисти терминал"   → executes cls (safe)
3. Say: "выполни git push"  → confirmation required
4. Say: "подтверждаю"       → executes
5. Say: "выполни rm -rf /"  → blocked (forbidden)
```
