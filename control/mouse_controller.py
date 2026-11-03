"""
Windows High-Performance Native Mouse Controller:
Direct Win32 API calls (user32.dll) for zero-latency, buttery-smooth cursor motion,
clicking, and scrolling. Includes screen bounding and emergency release safeguards.
"""
import ctypes
import time
from typing import Tuple, Optional
from utils.smoothing import ExponentialSmoother
from utils.logging_config import logger

user32 = ctypes.windll.user32

# Win32 Mouse Event Flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000


class MouseController:
    def __init__(self, smoothing_alpha: float = 0.45, sensitivity: float = 1.2):
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        self.smoother = ExponentialSmoother(alpha=smoothing_alpha)
        self.sensitivity = sensitivity
        self.is_mouse_down = False
        self._last_click_time = 0.0

        # Normalized Interaction ROI box (e.g. [0.15, 0.85] for comfortable edge-to-edge reach)
        self.roi_x_min = 0.15
        self.roi_x_max = 0.85
        self.roi_y_min = 0.15
        self.roi_y_max = 0.85

    def set_smoothing(self, alpha: float):
        self.smoother.alpha = max(0.05, min(1.0, alpha))

    def set_sensitivity(self, val: float):
        self.sensitivity = max(0.5, min(3.0, val))

    def move_cursor(self, norm_x: float, norm_y: float):
        """Map normalized camera coordinates to display coordinates with velocity-adaptive smoothing."""
        # Clamp to interaction ROI
        clamped_x = max(self.roi_x_min, min(self.roi_x_max, norm_x))
        clamped_y = max(self.roi_y_min, min(self.roi_y_max, norm_y))

        rel_x = (clamped_x - self.roi_x_min) / (self.roi_x_max - self.roi_x_min)
        rel_y = (clamped_y - self.roi_y_min) / (self.roi_y_max - self.roi_y_min)

        target_x = rel_x * self.screen_width
        target_y = rel_y * self.screen_height

        smooth_x, smooth_y = self.smoother.update(target_x, target_y)

        # Direct Win32 SetCursorPos call for instantaneous 0ms latency
        safe_x = int(max(0, min(self.screen_width - 1, round(smooth_x))))
        safe_y = int(max(0, min(self.screen_height - 1, round(smooth_y))))

        user32.SetCursorPos(safe_x, safe_y)

    def click(self, button: str = "left"):
        """Instant Win32 click with debounce protection."""
        now = time.monotonic()
        if now - self._last_click_time < 0.22:
            return
        self._last_click_time = now

        if button == "left":
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        logger.info(f"Win32 mouse click: {button}")

    def mouse_down(self, button: str = "left"):
        if not self.is_mouse_down:
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            self.is_mouse_down = True

    def mouse_up(self, button: str = "left"):
        if self.is_mouse_down:
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            self.is_mouse_down = False

    def scroll(self, amount: int):
        """Scroll vertical units via Win32 mouse_event."""
        # 120 is standard WHEEL_DELTA in Windows
        delta = int(amount * 2)
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

    def reset_state(self):
        """Emergency release of mouse button state."""
        if self.is_mouse_down:
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            self.is_mouse_down = False
        self.smoother.reset()
