"""
Gesture Control View:
Allows calibration, tuning smoothing & sensitivity sliders,
setting gesture hold/recognition delay, and displays full interactive cheat-sheet.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider, QPushButton, QScrollArea
)
from app.theme import PALETTE
from app.instructions_panel import GestureInstructionsPanel


class GestureControlView(QWidget):
    smoothing_changed = Signal(float)
    sensitivity_changed = Signal(float)
    hold_delay_changed = Signal(float)
    pc_control_toggled = Signal(bool)
    emergency_stop_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_pc_control_active = False
        self.is_emergency_stopped = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header bar
        header = QHBoxLayout()
        title = QLabel("Gesture Control & Tuning")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F3F5FA;")
        header.addWidget(title)
        header.addStretch()

        self.btn_estop = QPushButton("EMERGENCY STOP")
        self.btn_estop.setObjectName("StopButton")
        self.btn_estop.clicked.connect(self._trigger_estop)
        header.addWidget(self.btn_estop)

        main_layout.addLayout(header)

        # Top Control & Tuning Card
        tuning_card = QFrame()
        tuning_card.setObjectName("Card")
        tuning_vbox = QVBoxLayout(tuning_card)
        tuning_vbox.setContentsMargins(16, 16, 16, 16)
        tuning_vbox.setSpacing(12)

        # Safety control strip
        ctrl_strip = QHBoxLayout()
        self.lbl_status = QLabel("PC Control: OFF (Safe)")
        self.lbl_status.setStyleSheet(
            f"background-color: #172B1F; color: {PALETTE['green']}; padding: 6px 14px; border-radius: 6px; font-weight: bold;"
        )
        ctrl_strip.addWidget(self.lbl_status)

        self.btn_toggle = QPushButton("Enable PC Control")
        self.btn_toggle.setObjectName("PrimaryButton")
        self.btn_toggle.clicked.connect(self._toggle_control)
        ctrl_strip.addWidget(self.btn_toggle)

        ctrl_strip.addStretch()
        tuning_vbox.addLayout(ctrl_strip)

        # Sliders layout
        sliders_layout = QHBoxLayout()
        sliders_layout.setSpacing(20)

        # 1. Smoothing Slider
        smooth_box = QVBoxLayout()
        self.lbl_smooth = QLabel("Movement Smoothing: 0.45")
        self.lbl_smooth.setStyleSheet(f"color: {PALETTE['text_main']}; font-weight: 500;")
        self.slider_smooth = QSlider(Qt.Horizontal)
        self.slider_smooth.setRange(5, 80)
        self.slider_smooth.setValue(45)
        self.slider_smooth.valueChanged.connect(self._on_smooth_changed)
        smooth_box.addWidget(self.lbl_smooth)
        smooth_box.addWidget(self.slider_smooth)
        sliders_layout.addLayout(smooth_box)

        # 2. Sensitivity Slider
        sens_box = QVBoxLayout()
        self.lbl_sens = QLabel("Tracking Sensitivity: 1.2x")
        self.lbl_sens.setStyleSheet(f"color: {PALETTE['text_main']}; font-weight: 500;")
        self.slider_sens = QSlider(Qt.Horizontal)
        self.slider_sens.setRange(5, 30)
        self.slider_sens.setValue(12)
        self.slider_sens.valueChanged.connect(self._on_sens_changed)
        sens_box.addWidget(self.lbl_sens)
        sens_box.addWidget(self.slider_sens)
        sliders_layout.addLayout(sens_box)

        # 3. Gesture Recognition Hold Delay Slider (Analyzes gesture before executing)
        delay_box = QVBoxLayout()
        self.lbl_delay = QLabel("Gesture Confirm Delay: 0.28s")
        self.lbl_delay.setStyleSheet(f"color: {PALETTE['cyan']}; font-weight: 600;")
        self.slider_delay = QSlider(Qt.Horizontal)
        self.slider_delay.setRange(15, 60)  # 0.15s to 0.60s
        self.slider_delay.setValue(28)
        self.slider_delay.valueChanged.connect(self._on_delay_changed)
        delay_box.addWidget(self.lbl_delay)
        delay_box.addWidget(self.slider_delay)
        sliders_layout.addLayout(delay_box)

        tuning_vbox.addLayout(sliders_layout)
        main_layout.addWidget(tuning_card)

        # Instructions / Cheat-Sheet Panel
        self.instructions_panel = GestureInstructionsPanel()
        main_layout.addWidget(self.instructions_panel, stretch=1)

    def _toggle_control(self):
        if self.is_emergency_stopped:
            self.is_emergency_stopped = False
        self.is_pc_control_active = not self.is_pc_control_active
        self._update_ui_state()
        self.pc_control_toggled.emit(self.is_pc_control_active)

    def _trigger_estop(self):
        self.is_emergency_stopped = True
        self.is_pc_control_active = False
        self._update_ui_state()
        self.emergency_stop_clicked.emit()

    def set_control_state(self, active: bool, stopped: bool):
        self.is_pc_control_active = active
        self.is_emergency_stopped = stopped
        self._update_ui_state()

    def _update_ui_state(self):
        if self.is_emergency_stopped:
            self.lbl_status.setText("PC Control: STOPPED (E-Stop)")
            self.lbl_status.setStyleSheet(
                f"background-color: #2D1418; color: {PALETTE['red']}; padding: 6px 14px; border-radius: 6px; font-weight: bold;"
            )
            self.btn_toggle.setText("Reset & Enable Control")
        elif self.is_pc_control_active:
            self.lbl_status.setText("PC Control: ACTIVE")
            self.lbl_status.setStyleSheet(
                f"background-color: #382414; color: {PALETTE['amber']}; padding: 6px 14px; border-radius: 6px; font-weight: bold; border: 1px solid {PALETTE['amber']};"
            )
            self.btn_toggle.setText("Disable PC Control")
        else:
            self.lbl_status.setText("PC Control: OFF (Safe)")
            self.lbl_status.setStyleSheet(
                f"background-color: #172B1F; color: {PALETTE['green']}; padding: 6px 14px; border-radius: 6px; font-weight: bold;"
            )
            self.btn_toggle.setText("Enable PC Control")

    def _on_smooth_changed(self, val: int):
        alpha = val / 100.0
        self.lbl_smooth.setText(f"Movement Smoothing: {alpha:.2f}")
        self.smoothing_changed.emit(alpha)

    def _on_sens_changed(self, val: int):
        sens = val / 10.0
        self.lbl_sens.setText(f"Tracking Sensitivity: {sens:.1f}x")
        self.sensitivity_changed.emit(sens)

    def _on_delay_changed(self, val: int):
        sec = val / 100.0
        self.lbl_delay.setText(f"Gesture Confirm Delay: {sec:.2f}s")
        self.hold_delay_changed.emit(sec)
