"""
Dashboard widget: Displays live webcam feed, hand landmark tracking overlay,
metrics, and safety controls.
"""
from typing import List
import cv2
import numpy as np
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QCheckBox, QSizePolicy
)

from app.theme import PALETTE
from vision.hand_geometry import HandState, GestureEvent


class VideoWidget(QLabel):
    """Aspect-ratio-preserving video canvas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #06080D; border-radius: 8px;")
        self.setMinimumSize(QSize(480, 270))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._current_pixmap: QPixmap = QPixmap()

    def set_frame(self, frame_bgr: np.ndarray):
        h, w, ch = frame_bgr.shape
        bytes_per_line = ch * w
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self._current_pixmap = QPixmap.fromImage(qimg)
        self.update_display()

    def update_display(self):
        if not self._current_pixmap.isNull():
            scaled = self._current_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()


class DashboardView(QWidget):
    pc_control_toggled = Signal(bool)
    emergency_stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_pc_control_active = False
        self.is_emergency_stopped = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header bar
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F3F5FA;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Status badge
        self.cam_status_badge = QLabel("Camera: Connecting...")
        self.cam_status_badge.setObjectName("StatusPill")
        header_layout.addWidget(self.cam_status_badge)

        layout.addLayout(header_layout)

        # Central Area: Preview + Sidebar metrics
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Main video container card
        video_card = QFrame()
        video_card.setObjectName("Card")
        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(12, 12, 12, 12)

        self.video_widget = VideoWidget()
        video_layout.addWidget(self.video_widget)

        # Quick toggles under video
        video_controls = QHBoxLayout()
        video_controls.setSpacing(16)

        self.chk_landmarks = QCheckBox("Show Hand Skeleton (Landmarks)")
        self.chk_landmarks.setChecked(True)
        video_controls.addWidget(self.chk_landmarks)

        self.chk_mirror = QCheckBox("Mirror Preview")
        self.chk_mirror.setChecked(True)
        video_controls.addWidget(self.chk_mirror)

        video_controls.addStretch()
        video_layout.addLayout(video_controls)

        content_layout.addWidget(video_card, stretch=3)

        # Right sidebar info cards
        side_layout = QVBoxLayout()
        side_layout.setSpacing(12)

        # Status & Safety Card
        safety_card = QFrame()
        safety_card.setObjectName("Card")
        safety_vbox = QVBoxLayout(safety_card)
        safety_vbox.setContentsMargins(16, 16, 16, 16)
        safety_vbox.setSpacing(12)

        safety_title = QLabel("PC Control Safety")
        safety_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F3F5FA;")
        safety_vbox.addWidget(safety_title)

        # PC Control Status Indicator
        self.lbl_pc_control = QLabel("PC Control: OFF (Safe)")
        self.lbl_pc_control.setStyleSheet(
            f"background-color: #172B1F; color: {PALETTE['green']}; padding: 8px; border-radius: 6px; font-weight: bold;"
        )
        self.lbl_pc_control.setAlignment(Qt.AlignCenter)
        safety_vbox.addWidget(self.lbl_pc_control)

        # PC Control Toggle Button
        self.btn_toggle_control = QPushButton("Enable PC Control")
        self.btn_toggle_control.setObjectName("PrimaryButton")
        self.btn_toggle_control.clicked.connect(self._toggle_pc_control)
        safety_vbox.addWidget(self.btn_toggle_control)

        # Emergency Stop Button
        self.btn_estop = QPushButton("EMERGENCY STOP")
        self.btn_estop.setObjectName("StopButton")
        self.btn_estop.clicked.connect(self._trigger_estop)
        safety_vbox.addWidget(self.btn_estop)

        side_layout.addWidget(safety_card)

        # Metrics Card
        metrics_card = QFrame()
        metrics_card.setObjectName("Card")
        metrics_vbox = QVBoxLayout(metrics_card)
        metrics_vbox.setContentsMargins(16, 16, 16, 16)
        metrics_vbox.setSpacing(10)

        # FPS
        lbl_fps_hdr = QLabel("Frame Rate")
        lbl_fps_hdr.setObjectName("MetricLabel")
        self.val_fps = QLabel("0.0 FPS")
        self.val_fps.setObjectName("MetricValue")
        metrics_vbox.addWidget(lbl_fps_hdr)
        metrics_vbox.addWidget(self.val_fps)

        # Active Gesture
        lbl_gest_hdr = QLabel("Detected Gesture")
        lbl_gest_hdr.setObjectName("MetricLabel")
        self.val_gesture = QLabel("None")
        self.val_gesture.setObjectName("MetricValue")
        self.val_gesture.setStyleSheet(f"font-size: 16px; color: {PALETTE['cyan']};")
        metrics_vbox.addWidget(lbl_gest_hdr)
        metrics_vbox.addWidget(self.val_gesture)

        # Hands Detected
        lbl_hands_hdr = QLabel("Hands Detected")
        lbl_hands_hdr.setObjectName("MetricLabel")
        self.val_hands = QLabel("0 hands")
        self.val_hands.setObjectName("MetricValue")
        metrics_vbox.addWidget(lbl_hands_hdr)
        metrics_vbox.addWidget(self.val_hands)

        # Hand details label
        self.lbl_hand_details = QLabel("No hands in view")
        self.lbl_hand_details.setStyleSheet(f"color: {PALETTE['text_muted']}; font-size: 12px;")
        metrics_vbox.addWidget(self.lbl_hand_details)

        metrics_vbox.addStretch()
        side_layout.addWidget(metrics_card)

        content_layout.addLayout(side_layout, stretch=1)
        layout.addLayout(content_layout)

    def _toggle_pc_control(self):
        if self.is_emergency_stopped:
            self.is_emergency_stopped = False

        self.is_pc_control_active = not self.is_pc_control_active
        self._update_control_ui()
        self.pc_control_toggled.emit(self.is_pc_control_active)

    def _trigger_estop(self):
        self.is_emergency_stopped = True
        self.is_pc_control_active = False
        self._update_control_ui()
        self.emergency_stop_clicked.emit()

    def _update_control_ui(self):
        if self.is_emergency_stopped:
            self.lbl_pc_control.setText("PC Control: STOPPED (E-Stop)")
            self.lbl_pc_control.setStyleSheet(
                f"background-color: #2D1418; color: {PALETTE['red']}; padding: 8px; border-radius: 6px; font-weight: bold;"
            )
            self.btn_toggle_control.setText("Reset & Enable Control")
        elif self.is_pc_control_active:
            self.lbl_pc_control.setText("PC Control: ACTIVE")
            self.lbl_pc_control.setStyleSheet(
                f"background-color: #382414; color: {PALETTE['amber']}; padding: 8px; border-radius: 6px; font-weight: bold; border: 1px solid {PALETTE['amber']};"
            )
            self.btn_toggle_control.setText("Disable PC Control")
        else:
            self.lbl_pc_control.setText("PC Control: OFF (Safe)")
            self.lbl_pc_control.setStyleSheet(
                f"background-color: #172B1F; color: {PALETTE['green']}; padding: 8px; border-radius: 6px; font-weight: bold;"
            )
            self.btn_toggle_control.setText("Enable PC Control")

    def update_frame(self, frame: np.ndarray):
        self.video_widget.set_frame(frame)

    def update_fps(self, fps: float):
        self.val_fps.setText(f"{fps:.1f} FPS")

    def update_gestures(self, events: List[GestureEvent]):
        # Filter pointer_move out of the primary status label so user sees the actual gesture clearly
        action_names = [
            e.name.replace("_", " ").title()
            for e in events
            if e.phase in ("start", "update") and e.name != "pointer_move"
        ]
        if action_names:
            # Show the most confident / dominant single gesture rather than concatenating overlapping events
            self.val_gesture.setText(action_names[0])
        else:
            # If pointer_move is active alone, show Moving Cursor
            has_pointer = any(e.name == "pointer_move" for e in events)
            if has_pointer:
                self.val_gesture.setText("Moving Cursor")

    def update_hands(self, hands: List[HandState]):
        count = len(hands)
        self.val_hands.setText(f"{count} {'hand' if count == 1 else 'hands'}")
        if count == 0:
            self.lbl_hand_details.setText("No hands in view")
            self.val_gesture.setText("None")
        else:
            details = [f"{h.handedness} ({int(h.confidence * 100)}%)" for h in hands]
            self.lbl_hand_details.setText(" | ".join(details))

    def update_camera_status(self, active: bool, message: str):
        if active:
            self.cam_status_badge.setText(f"● {message}")
            self.cam_status_badge.setStyleSheet(f"color: {PALETTE['green']}; border-color: {PALETTE['green']};")
        else:
            self.cam_status_badge.setText(f"▲ {message}")
            self.cam_status_badge.setStyleSheet(f"color: {PALETTE['red']}; border-color: {PALETTE['red']};")
