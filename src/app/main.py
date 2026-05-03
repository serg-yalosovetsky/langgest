from __future__ import annotations

import argparse
import logging
import signal
import sys
import time

from app.event_bus import EventBus, Event
from app.storage.config_loader import load_config
from app.storage.event_log import EventLog
from app.storage.sqlite_store import SQLiteStore
from app.nlu.command_parser import CommandParser
from app.nlu.intent import Intent, IntentSource
from app.fusion.fusion_engine import FusionEngine
from app.policy.safety_policy import SafetyPolicy
from app.policy.confirmation import ConfirmationManager
from app.actions.dispatcher import CommandDispatcher
from app.actions.macro_adapter import MacroAdapter
from app.actions.shell_adapter import ShellAdapter
from app.context.active_window import get_active_window
from app.context.app_profiles import AppProfiles
from app.ui.debug_overlay import DebugOverlay

logger = logging.getLogger(__name__)

_RUNNING = True


def _setup_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Voice & Gesture Desktop Assistant")
    parser.add_argument("--config", default="config/app.yaml", help="Config file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-hardware", action="store_true", help="Disable microphone and camera (mock mode)")
    parser.add_argument("--no-tray", action="store_true", help="Disable system tray icon")
    args = parser.parse_args()

    config = load_config(args.config)
    _setup_logging(args.debug or config.app.debug_mode)
    logger.info("Starting Voice & Gesture Desktop Assistant")

    bus = EventBus()
    db = SQLiteStore(config.storage.db_path)
    event_log = EventLog(config.storage.log_path, config.security.log_clipboard_content)
    overlay = DebugOverlay()
    app_profiles = AppProfiles()

    # Command parsing
    cmd_parser = CommandParser("config/commands.yaml")
    fusion = FusionEngine()
    policy = SafetyPolicy(config.security.dangerous_commands_require_confirmation)
    dispatcher = CommandDispatcher(event_log=event_log)
    macro_adapter = MacroAdapter("config/macros.yaml")
    shell_adapter = ShellAdapter("config/shell_policy.yaml")

    # Wire shell.execute and macro handlers
    dispatcher.register("shell.execute", lambda i: shell_adapter.execute(i))
    dispatcher.register("shell.insert", lambda i: shell_adapter.insert(i.slots.get("command", "")))

    def _on_confirmed(intent: Intent) -> None:
        logger.info("Confirmed and executing: %s", intent.id)
        dispatcher.execute(intent)

    def _on_cancelled(intent: Intent) -> None:
        logger.info("Confirmation cancelled for: %s", intent.id)
        event_log.log_blocked(intent, "cancelled by user")

    confirmation = ConfirmationManager(_on_confirmed, _on_cancelled)

    # Audio service
    if not args.no_hardware:
        try:
            from app.audio.asr_ru import SherpaOnnxASR
            from app.audio.asr_en import FasterWhisperASR
            from app.audio.recorder import AudioRecorder

            asr_ru = SherpaOnnxASR(config.asr_ru.model_path)
            asr_en = FasterWhisperASR(config.asr_en.model)
            audio_recorder = AudioRecorder(config.audio, bus, asr_ru, asr_en)
            audio_recorder.start()
        except Exception as e:
            logger.warning("Audio service failed to start: %s", e)
    else:
        logger.info("Audio service disabled (--no-hardware)")

    # Camera / gesture service
    if not args.no_hardware and config.camera.enabled:
        try:
            from app.vision.camera import CameraCapture

            camera = CameraCapture(config.camera, config.gestures, bus, mock=False)
            camera.start()
        except Exception as e:
            logger.warning("Camera service failed to start: %s", e)
    else:
        logger.info("Camera service disabled")

    # Tray icon (non-blocking; runs in background via Qt event loop integration)
    tray = None
    if not args.no_tray:
        try:
            from app.ui.tray import TrayIcon

            def quit_handler() -> None:
                global _RUNNING
                _RUNNING = False
                bus.stop()

            tray = TrayIcon(on_quit=quit_handler)
            tray.start()
        except Exception as e:
            logger.debug("Tray icon unavailable: %s", e)

    # Graceful shutdown on Ctrl+C
    def _sigint_handler(sig, frame) -> None:
        global _RUNNING
        logger.info("Shutting down...")
        _RUNNING = False
        bus.stop()

    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGTERM, _sigint_handler)

    logger.info("Ready. Listening for commands...")

    # Main event loop
    for event in bus.listen():
        if not _RUNNING:
            break

        intent: Intent | None = None

        if event.type == "voice.text":
            text = event.payload.get("text", "")
            language = event.payload.get("language", config.app.language_default)

            # First check if this is a confirmation for a pending dangerous command
            if confirmation.has_pending():
                if confirmation.try_confirm(text, language):
                    continue

            intent = cmd_parser.parse(text, language)
            if intent is None:
                logger.debug("No intent for: %r", text)
                continue

        elif event.type == "gesture.detected":
            gesture_name = event.payload.get("gesture", "")
            confidence = event.payload.get("confidence", 1.0)
            intent = Intent.from_gesture(gesture_name, confidence)
            event_log.log_gesture(gesture_name, confidence, accepted=True)

        if intent is None:
            continue

        final_intent = fusion.add(intent)
        if final_intent is None:
            continue

        window_info = get_active_window()
        active_app = window_info.process_name
        profile = app_profiles.detect_profile(window_info)

        decision = policy.evaluate(final_intent)

        overlay.add({
            "intent": final_intent.id,
            "confidence": final_intent.confidence,
            "decision": "allowed" if decision.allowed else ("confirm" if decision.requires_confirmation else "blocked"),
            "app": active_app,
            "profile": profile,
        })

        if decision.allowed:
            if final_intent.id.startswith("macro."):
                macro_adapter.execute_macro(final_intent)
                event_log.log_intent(final_intent, active_app=active_app)
            else:
                dispatcher.execute(final_intent, active_app=active_app)
        elif decision.requires_confirmation:
            confirmation.request(final_intent)
            event_log.log_confirmation_requested(final_intent)
            if tray:
                tray.show_notification(
                    "Подтверждение требуется",
                    f"Команда: {final_intent.id}\nСкажите 'подтверждаю' для выполнения",
                )
            else:
                print(f"\n[CONFIRM REQUIRED] {final_intent.id} — say 'подтверждаю' to execute")
        else:
            event_log.log_blocked(final_intent, decision.reason)
            logger.info("Blocked: %s — %s", final_intent.id, decision.reason)

    logger.info("Voice & Gesture Assistant stopped")


if __name__ == "__main__":
    main()
