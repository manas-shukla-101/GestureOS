"""
Vision worker running on a background QThread to keep the Qt UI responsive.
Integrates HandTracker, GestureRecognizer, and ActionDispatcher.
Dedicated solely to tracking, gesture classification, and PC control.
"""
import time
from typing import List, Optional
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal, Slot

from vision.camera_manager import CameraManager
from vision.hand_tracker import HandTracker
from vision.hand_geometry import HandState, GestureEvent
from vision.gesture_recognition import GestureRecognizer
from control.action_dispatcher import ActionDispatcher
from utils.performance import FPSCounter
from utils.logging_config import logger


class VisionWorker(QThread):
    # Signals to communicate cleanly with GUI thread
    frame_ready = Signal(np.ndarray)
    hands_detected = Signal(list)
    gestures_recognized = Signal(list)
    fps_updated = Signal(float)
    camera_status = Signal(bool, str)

    def __init__(self, camera_index: int = 0, model_path: str = "models/hand_landmarker.task"):
        super().__init__()
        self.camera_index = camera_index
        self.model_path = model_path
        self._running = False

        # Core pipeline components
        self.camera_manager = CameraManager(camera_index=camera_index)
        self.hand_tracker: Optional[HandTracker] = None
        self.gesture_recognizer = GestureRecognizer()
        self.action_dispatcher = ActionDispatcher()
        self.fps_counter = FPSCounter()

        # UI toggles
        self.show_landmarks = True
        self.mirror_preview = True

    def run(self):
        self._running = True
        logger.info("VisionWorker thread started.")

        try:
            self.hand_tracker = HandTracker(model_path=self.model_path)
        except Exception as e:
            logger.error(f"Failed to initialize HandTracker in worker: {e}")
            self.camera_status.emit(False, f"Hand tracker error: {e}")
            self._running = False
            return

        if not self.camera_manager.open(self.camera_index):
            self.camera_status.emit(False, f"Failed to open camera {self.camera_index}")
            self._running = False
            return

        self.camera_status.emit(True, f"Camera {self.camera_index} Active")

        while self._running:
            success, frame = self.camera_manager.read_frame()
            if not success or frame is None:
                time.sleep(0.01)
                continue

            if self.mirror_preview:
                frame = cv2.flip(frame, 1)

            # 1. Hand Tracking
            hands = self.hand_tracker.process_frame(frame)
            self.hands_detected.emit(hands)

            # 2. Gesture Recognition
            events = self.gesture_recognizer.recognize(hands)
            if events:
                self.gestures_recognized.emit(events)

            # 3. Action Dispatcher (Safe OS PC control execution)
            self.action_dispatcher.process(hands, events)

            # 4. Hand Landmarks Overlay
            display_frame = frame.copy()
            if self.show_landmarks and hands:
                self.hand_tracker.draw_landmarks(display_frame, hands)

            # 5. Metrics & Frame dispatch
            current_fps = self.fps_counter.tick()
            self.fps_updated.emit(current_fps)
            self.frame_ready.emit(display_frame)

            time.sleep(0.001)

        self.camera_manager.release()
        logger.info("VisionWorker thread exiting.")

    def stop(self):
        logger.info("Stopping VisionWorker...")
        self._running = False
        self.action_dispatcher.disable_control()
        self.wait(2000)

    @Slot(int)
    def switch_camera(self, new_index: int):
        self.camera_index = new_index
        if self._running:
            self.camera_manager.open(self.camera_index)

    @Slot(bool)
    def set_show_landmarks(self, enabled: bool):
        self.show_landmarks = enabled

    @Slot(bool)
    def set_mirror_preview(self, enabled: bool):
        self.mirror_preview = enabled

    @Slot(bool)
    def set_pc_control_enabled(self, enabled: bool):
        if enabled:
            self.action_dispatcher.enable_control()
        else:
            self.action_dispatcher.disable_control()

    @Slot()
    def trigger_emergency_stop(self):
        self.action_dispatcher.trigger_emergency_stop()

    @Slot()
    def clear_emergency_stop(self):
        self.action_dispatcher.clear_emergency_stop()
