from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Simple settings window (PySide6). Stub for MVP."""

    def show(self) -> None:
        try:
            from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout  # type: ignore

            dialog = QDialog()
            dialog.setWindowTitle("Voice & Gesture Assistant — Settings")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Settings UI coming soon.\nEdit config/app.yaml to configure."))
            dialog.setLayout(layout)
            dialog.exec()
        except ImportError:
            logger.info("Settings window unavailable (PySide6 not installed)")
