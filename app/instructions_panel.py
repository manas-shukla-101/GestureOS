"""
Instructions, Gesture Reference & Guides Widget for GestureOS.
Displays clear cheat-sheet cards showing postures, shortcuts, and full PC control combinations.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QGridLayout
)
from app.theme import PALETTE


class InstructionCard(QFrame):
    """Card displaying a specific gesture posture, combination, and resulting action."""
    def __init__(self, title: str, gesture_badge: str, description: str, tips: str, badge_color=None, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        color = badge_color or PALETTE['cyan']
        self.setStyleSheet(f"background-color: {PALETTE['surface']}; border-radius: 10px; padding: 12px;")

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        header = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F3F5FA;")
        header.addWidget(lbl_title)

        header.addStretch()

        badge = QLabel(f" {gesture_badge} ")
        badge.setStyleSheet(
            f"background-color: #17243B; color: {color}; border: 1px solid {color}; border-radius: 5px; font-weight: bold; font-size: 11px; padding: 2px 6px;"
        )
        header.addWidget(badge)
        layout.addLayout(header)

        desc = QLabel(description)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {PALETTE['text_main']}; font-size: 13px;")
        layout.addWidget(desc)

        tip_label = QLabel(f"💡 {tips}")
        tip_label.setWordWrap(True)
        tip_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-size: 11px; font-style: italic;")
        layout.addWidget(tip_label)


class GestureInstructionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        container_layout.setContentsMargins(10, 10, 10, 10)

        # Overview banner
        banner = QFrame()
        banner.setObjectName("CardElevated")
        banner_vbox = QVBoxLayout(banner)
        banner_vbox.setContentsMargins(14, 14, 14, 14)
        banner_title = QLabel("Complete GestureOS Hands-Free PC Controls")
        banner_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {PALETTE['cyan']};")
        banner_vbox.addWidget(banner_title)

        banner_text = QLabel(
            "Control your Windows desktop completely hands-free using your webcam. "
            "PC Control is opt-in for safety and must be toggled ON. Below is the comprehensive command reference."
        )
        banner_text.setWordWrap(True)
        banner_text.setStyleSheet(f"color: {PALETTE['text_muted']}; font-size: 12px;")
        banner_vbox.addWidget(banner_text)
        container_layout.addWidget(banner)

        # Category 1: Mouse & Clicking
        cat1_label = QLabel("1. Mouse Tracking & Multi-Finger Clicks")
        cat1_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {PALETTE['green']};")
        container_layout.addWidget(cat1_label)

        grid1 = QGridLayout()
        grid1.setSpacing(12)

        grid1.addWidget(InstructionCard(
            title="Move Cursor",
            gesture_badge="Index Finger Pointing ☝️",
            description="Extend your index finger. Direct Win32 hardware positioning delivers silky smooth motion with 0ms latency.",
            tips="Center of camera frame maps smoothly to entire screen."
        ), 0, 0)

        grid1.addWidget(InstructionCard(
            title="Left Click",
            gesture_badge="Thumb + Index Pinch 🤏",
            description="Pinch thumb tip and index fingertip together to trigger a standard left mouse click.",
            tips="Movement remains active during pinch."
        ), 0, 1)

        grid1.addWidget(InstructionCard(
            title="Right Click",
            gesture_badge="Thumb + Middle Pinch ✌️",
            description="Pinch thumb tip and middle fingertip together to trigger a context menu right click.",
            tips="Use on icons, files, or desktop."
        ), 1, 0)

        grid1.addWidget(InstructionCard(
            title="Double Click",
            gesture_badge="Thumb + Ring Pinch 💍",
            description="Pinch thumb tip and ring fingertip together to perform an instantaneous double click.",
            tips="Opens folders, applications, and files immediately."
        ), 1, 1)

        container_layout.addLayout(grid1)

        # Category 2: Scrolling & Window Navigation
        cat2_label = QLabel("2. Scrolling & Window Management")
        cat2_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {PALETTE['cyan']};")
        container_layout.addWidget(cat2_label)

        grid2 = QGridLayout()
        grid2.setSpacing(12)

        grid2.addWidget(InstructionCard(
            title="Scroll UP",
            gesture_badge="Peace Sign (2 fingers) ✌️",
            description="Hold index and middle fingers in a 'V' shape to scroll upward smoothly.",
            tips="Scroll feeds, PDFs, and long documents.",
            badge_color=PALETTE['cyan']
        ), 0, 0)

        grid2.addWidget(InstructionCard(
            title="Scroll DOWN",
            gesture_badge="Three Fingers (3 fingers) 🖐️",
            description="Extend index, middle, and ring fingers to scroll content downward.",
            tips="Switch between 2 and 3 fingers to navigate up and down.",
            badge_color=PALETTE['cyan']
        ), 0, 1)

        grid2.addWidget(InstructionCard(
            title="Switch Windows",
            gesture_badge="Four Fingers 🖖",
            description="Extend 4 fingers (thumb tucked) to execute Alt + Tab and switch between active application windows.",
            tips="Cycles between your current running apps.",
            badge_color=PALETTE['cyan']
        ), 1, 0)

        grid2.addWidget(InstructionCard(
            title="Show / Hide Desktop",
            gesture_badge="Closed Fist ✊",
            description="Close all fingers into a tight fist to trigger Win + D (minimizes all windows to reveal desktop).",
            tips="Make a fist again to restore windows.",
            badge_color=PALETTE['cyan']
        ), 1, 1)

        container_layout.addLayout(grid2)

        # Category 3: Application Launching & Utilities
        cat3_label = QLabel("3. Application Launchers & System Shortcuts")
        cat3_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {PALETTE['amber']};")
        container_layout.addWidget(cat3_label)

        grid3 = QGridLayout()
        grid3.setSpacing(12)

        grid3.addWidget(InstructionCard(
            title="Open Web Browser",
            gesture_badge="Thumbs Up 👍",
            description="Extend thumb upward with other fingers folded to open your default browser.",
            tips="Cooldown protection prevents duplicate tabs.",
            badge_color=PALETTE['amber']
        ), 0, 0)

        grid3.addWidget(InstructionCard(
            title="Open Calculator",
            gesture_badge="Rock Horns 🤘",
            description="Extend index and pinky fingers to launch Windows Calculator instantly.",
            tips="Quick access for calculations.",
            badge_color=PALETTE['amber']
        ), 0, 1)

        grid3.addWidget(InstructionCard(
            title="Open Notepad",
            gesture_badge="Pinky Up 🤙",
            description="Extend only your pinky finger to open a new Notepad window.",
            tips="Great for jotting rapid notes.",
            badge_color=PALETTE['amber']
        ), 1, 0)

        grid3.addWidget(InstructionCard(
            title="Open File Explorer",
            gesture_badge="Call Me / Shaka 🤙",
            description="Extend thumb and pinky simultaneously (shaka sign) to open Windows File Explorer.",
            tips="Browse documents and files quickly.",
            badge_color=PALETTE['amber']
        ), 1, 1)

        grid3.addWidget(InstructionCard(
            title="Take Screenshot",
            gesture_badge="Gun / L-Shape 🔫",
            description="Form an 'L' shape with thumb and index finger extended to open Snipping Tool (Win + Shift + S).",
            tips="Snip any screen region effortlessly.",
            badge_color=PALETTE['amber']
        ), 2, 0)

        grid3.addWidget(InstructionCard(
            title="Media Play / Pause",
            gesture_badge="OK Sign 👌",
            description="Form an 'OK' circle with thumb & index while holding 3 fingers up to toggle multimedia play/pause.",
            tips="Controls Spotify, YouTube, and media players.",
            badge_color=PALETTE['amber']
        ), 2, 1)

        container_layout.addLayout(grid3)

        # Category 4: Safety Controls
        cat4_label = QLabel("4. Safety & Fail-Safes")
        cat4_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {PALETTE['red']};")
        container_layout.addWidget(cat4_label)

        grid4 = QGridLayout()
        grid4.setSpacing(12)

        grid4.addWidget(InstructionCard(
            title="Safety Pause / Neutral",
            gesture_badge="Open Palm ✋",
            description="Open all 5 fingers to pause and rest without moving the cursor or clicking.",
            tips="Use whenever repositioning your arm comfortably.",
            badge_color=PALETTE['green']
        ), 0, 0)

        grid4.addWidget(InstructionCard(
            title="Emergency Stop",
            gesture_badge="Red Stop Button 🛑",
            description="Immediately disengages all PC control and releases all held mouse buttons with 0ms delay.",
            tips="Automatic watchdog also releases clicks if hands leave the frame for > 400ms.",
            badge_color=PALETTE['red']
        ), 0, 1)

        container_layout.addLayout(grid4)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
