# Security & Privacy

## Principles

1. **Local processing by default** — no audio/video sent to the cloud.
2. **No cloud upload** unless explicitly enabled in config.
3. **Dangerous commands require confirmation** — `shell.execute`, `system.*`.
4. **Clipboard content redacted** in all logs (only length is stored).
5. **Raw audio/video not stored** by default (`log_audio: false`, `log_video: false`).
6. **Shell execution policy-gated** — allowlist in `config/shell_policy.yaml`.
7. **Risk levels enforced** — FORBIDDEN commands blocked unconditionally.

## Risk levels

| Level | Examples | Default behavior |
|---|---|---|
| SAFE | volume, media, browser navigation | Execute immediately |
| MEDIUM | close tab, clipboard ops, shell insert | Execute only if confidence ≥ 0.80 |
| DANGEROUS | shell.execute | Require voice confirmation within 30 s |
| FORBIDDEN | system.format, system.destroy | Always blocked |

## Shell policy

Controlled by `config/shell_policy.yaml`:

- `auto_execute_allowed`: glob patterns for commands that run without confirmation.
- `require_confirmation_patterns`: patterns that always require confirmation.
- `forbidden_patterns`: patterns that are permanently blocked.

## What is never logged

- Raw audio data
- Raw video frames
- Full clipboard content (only `length` and `[redacted]` preview)
- Passwords or API keys typed by user
- Screenshots

## Confirmation flow

```
User: "выполни docker compose down"
System: CONFIRM REQUIRED — say 'подтверждаю' to execute
User: "подтверждаю"
System: executes
```

Confirmation times out after 30 seconds. User can also cancel via tray menu.
