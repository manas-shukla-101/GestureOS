"""
Main application window hosting sidebar navigation and primary functional views.
Magic mode has been cleanly removed to focus purely on high-performance Hands-Free PC Control.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QLabel, QStackedWidget
)

from app.theme import MAIN_STYLESHEET, PALETTE
from app.dashboard import DashboardView
from app.gesture_control_view import GestureControlView
from app.settings_view import SettingsView
from config.settings_manager import SettingsManager
from vision.vision_worker import VisionWorker
from utils.logging_config import logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestureOS — Hands-Free PC Control Console")
        self.resize(1260, 780)
        self.setMinimumSize(QSize(1000, 650))
        self.setStyleSheet(MAIN_STYLESHEET)

        # Settings
        self.settings_manager = SettingsManager()

        # Background Vision Worker
        cam_idx = self.settings_manager.get("camera", "index", 0)
        self.vision_worker: VisionWorker = VisionWorker(camera_index=cam_idx)
        self.vision_worker.set_mirror_preview(self.settings_manager.get("camera", "mirror", True))
        self.vision_worker.set_show_landmarks(self.settings_manager.get("camera", "show_landmarks", True))

        self.init_ui()
        self.connect_signals()
        self.start_vision()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(8)

        # Brand
        brand_label = QLabel("GestureOS")
        brand_label.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {PALETTE['cyan']}; letter-spacing: 1.5px; padding-bottom: 16px;"
        )
        sidebar_layout.addWidget(brand_label)

        # Navigation buttons (Focused strictly on PC Control & Settings)
        self.nav_buttons = []
        self.btn_nav_dashboard = QPushButton("  Dashboard")
        self.btn_nav_dashboard.setObjectName("NavButton")
        self.btn_nav_dashboard.setCheckable(True)
        self.btn_nav_dashboard.setChecked(True)
        self.btn_nav_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.nav_buttons.append(self.btn_nav_dashboard)

        self.btn_nav_control = QPushButton("  Gesture Controls")
        self.btn_nav_control.setObjectName("NavButton")
        self.btn_nav_control.setCheckable(True)
        self.btn_nav_control.clicked.connect(lambda: self.switch_page(1))
        self.nav_buttons.append(self.btn_nav_control)

        self.btn_nav_settings = QPushButton("  Settings")
        self.btn_nav_settings.setObjectName("NavButton")
        self.btn_nav_settings.setCheckable(True)
        self.btn_nav_settings.clicked.connect(lambda: self.switch_page(2))
        self.nav_buttons.append(self.btn_nav_settings)

        for btn in self.nav_buttons:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Version tag
        version_label = QLabel("v1.0.0 PC Control")
        version_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-size: 11px;")
        sidebar_layout.addWidget(version_label)

        root_layout.addWidget(sidebar)

        # Stacked Pages
        self.pages = QStackedWidget()

        # Page 0: Live Dashboard
        self.dashboard_view = DashboardView()
        self.pages.addWidget(self.dashboard_view)

        # Page 1: Gesture Controls & Complete Reference
        self.gesture_view = GestureControlView()
        self.pages.addWidget(self.gesture_view)

        # Page 2: Settings
        self.settings_view = SettingsView(settings_manager=self.settings_manager)
        self.pages.addWidget(self.settings_view)

        root_layout.addWidget(self.pages)

    def switch_page(self, index: int):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def connect_signals(self):
        # VisionWorker -> Dashboard View
        self.vision_worker.frame_ready.connect(self.dashboard_view.update_frame)
        self.vision_worker.fps_updated.connect(self.dashboard_view.update_fps)
        self.vision_worker.hands_detected.connect(self.dashboard_view.update_hands)
        self.vision_worker.gestures_recognized.connect(self.dashboard_view.update_gestures)
        self.vision_worker.camera_status.connect(self.dashboard_view.update_camera_status)

        # Dashboard View -> VisionWorker
        self.dashboard_view.chk_landmarks.toggled.connect(self.vision_worker.set_show_landmarks)
        self.dashboard_view.chk_mirror.toggled.connect(self.vision_worker.set_mirror_preview)

        # Sync PC Control between Dashboard and GestureControlView
        self.dashboard_view.pc_control_toggled.connect(self._sync_control_enabled)
        self.dashboard_view.emergency_stop_clicked.connect(self._sync_emergency_stop)
        self.gesture_view.pc_control_toggled.connect(self._sync_control_enabled)
        self.gesture_view.emergency_stop_clicked.connect(self._sync_emergency_stop)

        # Sliders tuning
        self.gesture_view.smoothing_changed.connect(
            lambda val: self.vision_worker.action_dispatcher.mouse_controller.set_smoothing(val)
        )
        self.gesture_view.sensitivity_changed.connect(
            lambda val: self.vision_worker.action_dispatcher.mouse_controller.set_sensitivity(val)
        )
        self.gesture_view.hold_delay_changed.connect(
            lambda val: self.vision_worker.gesture_recognizer.set_hold_delay(val)
        )

        # Settings View
        self.settings_view.camera_changed.connect(self.vision_worker.switch_camera)
        self.settings_view.mirror_toggled.connect(self.vision_worker.set_mirror_preview)
        self.settings_view.landmarks_toggled.connect(self.vision_worker.set_show_landmarks)

    def _sync_control_enabled(self, enabled: bool):
        self.vision_worker.set_pc_control_enabled(enabled)
        self.dashboard_view.is_pc_control_active = enabled
        self.dashboard_view.is_emergency_stopped = False
        self.dashboard_view._update_control_ui()
        self.gesture_view.set_control_state(enabled, False)

    def _sync_emergency_stop(self):
        self.vision_worker.trigger_emergency_stop()
        self.dashboard_view.is_pc_control_active = False
        self.dashboard_view.is_emergency_stopped = True
        self.dashboard_view._update_control_ui()
        self.gesture_view.set_control_state(False, True)

    def start_vision(self):
        logger.info("Starting background vision worker thread...")
        self.vision_worker.start()

    def closeEvent(self, event):
        logger.info("Application closing: stopping worker and releasing camera...")
        self.vision_worker.stop()
        event.accept()
