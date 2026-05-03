from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

from app.event_bus import EventBus, Event
from app.storage.config_loader import CameraConfig, GestureConfig
from app.vision.mediapipe_hands import MPHandsDetector
from app.vision.gesture_classifier import GestureClassifier
from app.vision.gesture_smoothing import GestureSmoothing

logger = logging.getLogger(__name__)


class CameraCapture:
    """Captures frames from webcam, runs gesture pipeline, posts gesture.detected events."""

    def __init__(
        self,
        camera_config: CameraConfig,
        gesture_config: GestureConfig,
        bus: EventBus,
        mock: bool = False,
    ) -> None:
        self._cam_cfg = camera_config
        self._gest_cfg = gesture_config
        self._bus = bus
        self._mock = mock
        self._detector = MPHandsDetector()
        self._classifier = GestureClassifier()
        self._smoother = GestureSmoothing(
            min_stable_frames=gesture_config.min_stable_frames,
            confidence_threshold=gesture_config.confidence_threshold,
            cooldown_ms=gesture_config.cooldown_ms,
        )
        self._thread: threading.Thread | None = None
        self._running = False
        self._injected_frames: list["np.ndarray"] = []

    def start(self) -> None:
        if not self._cam_cfg.enabled and not self._mock:
            logger.info("Camera disabled in config")
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="CameraCapture")
        self._thread.start()
        logger.info("CameraCapture started (mock=%s)", self._mock)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        self._detector.close()

    def inject_frame(self, frame_rgb: "np.ndarray") -> None:
        """Inject a synthetic frame for testing."""
        self._injected_frames.append(frame_rgb)

    def _run(self) -> None:
        if self._mock:
            self._run_mock()
        else:
            self._run_real()

    def _run_mock(self) -> None:
        import numpy as np

        while self._running:
            if self._injected_frames:
                frame = self._injected_frames.pop(0)
                self._process_frame(frame)
            else:
                time.sleep(0.033)

    def _run_real(self) -> None:
        try:
            import cv2  # type: ignore
        except ImportError:
            logger.warning("opencv-python not installed — camera unavailable")
            return

        cap = cv2.VideoCapture(self._cam_cfg.device_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._cam_cfg.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._cam_cfg.height)
        cap.set(cv2.CAP_PROP_FPS, self._cam_cfg.fps)

        if not cap.isOpened():
            logger.warning("Cannot open camera device %d", self._cam_cfg.device_index)
            return

        try:
            while self._running:
                ret, frame_bgr = cap.read()
                if not ret:
                    time.sleep(0.033)
                    continue
                frame_rgb = frame_bgr[:, :, ::-1]
                self._process_frame(frame_rgb)
        finally:
            cap.release()

    def _process_frame(self, frame_rgb: "np.ndarray") -> None:
        hands = self._detector.detect(frame_rgb)
        if not hands:
            self._smoother.update(None)
            return

        hand = hands[0]
        raw_gesture = self._classifier.classify(hand)
        accepted = self._smoother.update(raw_gesture)

        if accepted:
            self._bus.post(Event(
                type="gesture.detected",
                payload={"gesture": accepted.name, "confidence": accepted.confidence},
            ))
            logger.debug("Gesture accepted: %s (%.2f)", accepted.name, accepted.confidence)
