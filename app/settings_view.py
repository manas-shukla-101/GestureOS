"""
Settings Panel View:
Configures camera options, performance settings, and persists them via SettingsManager.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox, QCheckBox, QPushButton
)
from app.theme import PALETTE
from config.settings_manager import SettingsManager
from vision.camera_manager import CameraManager


class SettingsView(QWidget):
    camera_changed = Signal(int)
    mirror_toggled = Signal(bool)
    landmarks_toggled = Signal(bool)

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #F3F5FA;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Camera Settings Card
        cam_card = QFrame()
        cam_card.setObjectName("Card")
        cam_vbox = QVBoxLayout(cam_card)
        cam_vbox.setContentsMargins(16, 16, 16, 16)
        cam_vbox.setSpacing(12)

        cam_title = QLabel("Webcam Configuration")
        cam_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #F3F5FA;")
        cam_vbox.addWidget(cam_title)

        # Camera selector
        row1 = QHBoxLayout()
        lbl_cam = QLabel("Selected Camera Device:")
        lbl_cam.setStyleSheet(f"color: {PALETTE['text_main']};")
        row1.addWidget(lbl_cam)

        self.combo_cam = QComboBox()
        self.combo_cam.setStyleSheet(
            f"background-color: {PALETTE['surface_elevated']}; color: #F3F5FA; border: 1px solid {PALETTE['border']}; border-radius: 6px; padding: 4px 8px;"
        )
        # Scan devices
        available_cams = CameraManager.enumerate_cameras(max_tested=3)
        for cam_id in available_cams:
            self.combo_cam.addItem(f"Camera Device {cam_id}", cam_id)

        saved_cam = self.settings.get("camera", "index", 0)
        idx = self.combo_cam.findData(saved_cam)
        if idx >= 0:
            self.combo_cam.setCurrentIndex(idx)
        self.combo_cam.currentIndexChanged.connect(self._on_camera_changed)

        row1.addWidget(self.combo_cam)
        row1.addStretch()
        cam_vbox.addLayout(row1)

        # Mirror toggle
        self.chk_mirror = QCheckBox("Mirror camera preview horizontally")
        self.chk_mirror.setChecked(self.settings.get("camera", "mirror", True))
        self.chk_mirror.toggled.connect(self._on_mirror_toggled)
        cam_vbox.addWidget(self.chk_mirror)

        # Landmarks toggle
        self.chk_lms = QCheckBox("Render MediaPipe hand skeleton overlay")
        self.chk_lms.setChecked(self.settings.get("camera", "show_landmarks", True))
        self.chk_lms.toggled.connect(self._on_landmarks_toggled)
        cam_vbox.addWidget(self.chk_lms)

        layout.addWidget(cam_card)

        # Safety & Reset Card
        safe_card = QFrame()
        safe_card.setObjectName("Card")
        safe_vbox = QVBoxLayout(safe_card)
        safe_vbox.setContentsMargins(16, 16, 16, 16)
        safe_vbox.setSpacing(10)

        safe_title = QLabel("Defaults & Storage")
        safe_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #F3F5FA;")
        safe_vbox.addWidget(safe_title)

        lbl_desc = QLabel("Configuration is persistently stored in config/settings.json.")
        lbl_desc.setStyleSheet(f"color: {PALETTE['text_muted']}; font-size: 12px;")
        safe_vbox.addWidget(lbl_desc)

        btn_reset = QPushButton("Reset All to Default Settings")
        btn_reset.setObjectName("PrimaryButton")
        btn_reset.clicked.connect(self._reset_defaults)
        safe_vbox.addWidget(btn_reset)

        layout.addWidget(safe_card)
        layout.addStretch()

    def _on_camera_changed(self, index: int):
        cam_id = self.combo_cam.itemData(index)
        self.settings.set("camera", "index", cam_id)
        self.camera_changed.emit(cam_id)

    def _on_mirror_toggled(self, checked: bool):
        self.settings.set("camera", "mirror", checked)
        self.mirror_toggled.emit(checked)

    def _on_landmarks_toggled(self, checked: bool):
        self.settings.set("camera", "show_landmarks", checked)
        self.landmarks_toggled.emit(checked)

    def _reset_defaults(self):
        from config.settings_manager import DEFAULT_SETTINGS
        self.settings.save(DEFAULT_SETTINGS.copy())
        self.chk_mirror.setChecked(True)
        self.chk_lms.setChecked(True)

