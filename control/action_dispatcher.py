"""
Action Dispatcher: Central authority and gatekeeper for all PC control events.
Strict safety rules:
- PC Control is OFF by default.
- Emergency stop halts and releases all inputs immediately.
- Automatic release on hand loss timeout.
- Mappings:
    - pointer_move: Move cursor with 0ms Win32 hardware positioning
    - pinch_index (start): Left Click
    - pinch_middle (start): Right Click
    - pinch_ring (start): Double Click
    - peace (hold): Scroll UP
    - three_fingers (hold): Scroll DOWN
    - four_fingers (start): Switch Window (Alt + Tab)
    - fist (start): Show Desktop (Win + D)
    - thumbs_up (start): Launch Web Browser
    - rock_horns (start): Launch Calculator
    - pinky_up (start): Launch Notepad
    - call_me (start): Launch File Explorer
    - gun_l_shape (start): Take Screenshot (Win + Shift + S)
    - ok_sign (start): Media Play / Pause
"""
import time
from typing import List, Optional
from vision.hand_geometry import GestureEvent, HandState
from control.mouse_controller import MouseController
from control.system_controller import SystemActionController
from utils.logging_config import logger


class ActionDispatcher:
    def __init__(self, mouse_controller: Optional[MouseController] = None):
        self.mouse_controller = mouse_controller or MouseController()

        # Safety states
        self.control_enabled = False
        self.emergency_stop = False

        # Hand loss watchdog
        self.last_valid_hand_time = time.monotonic()
        self.hand_loss_timeout = 0.4

        # Action cooldowns
        self._last_scroll_time = 0.0
        self._last_discrete_action_time = 0.0
        self.action_cooldown = 1.3  # 1.3s cooldown between discrete system/app triggers

    def enable_control(self):
        if self.emergency_stop:
            logger.warning("Cannot enable PC control while Emergency Stop is active.")
            return False
        self.control_enabled = True
        logger.info("PC Control ENABLED.")
        return True

    def disable_control(self):
        self.control_enabled = False
        self.mouse_controller.reset_state()
        logger.info("PC Control DISABLED.")

    def trigger_emergency_stop(self):
        self.emergency_stop = True
        self.control_enabled = False
        self.mouse_controller.reset_state()
        logger.warning("EMERGENCY STOP TRIGGERED: All PC control disabled and released.")

    def clear_emergency_stop(self):
        self.emergency_stop = False
        self.control_enabled = False
        self.mouse_controller.reset_state()
        logger.info("Emergency Stop cleared.")

    def process(self, hands: List[HandState], events: List[GestureEvent]):
        now = time.monotonic()

        # Safety hand-loss watchdog
        active_hands = [h for h in hands if h.is_valid]
        if active_hands:
            self.last_valid_hand_time = now
        else:
            if now - self.last_valid_hand_time > self.hand_loss_timeout:
                self.mouse_controller.reset_state()

        # Gate: if PC Control disabled or E-Stop, take zero OS actions
        if not self.control_enabled or self.emergency_stop:
            return

        for event in events:
            # 1. Cursor Movement
            if event.name == "pointer_move" and event.phase == "update":
                norm_x = event.payload.get("x")
                norm_y = event.payload.get("y")
                if norm_x is not None and norm_y is not None:
                    self.mouse_controller.move_cursor(norm_x, norm_y)

            # 2. Clicks (Pinch Index = Left, Pinch Middle = Right, Pinch Ring = Double Click)
            elif event.name == "pinch_index" and event.phase == "start":
                self.mouse_controller.click("left")

            elif event.name == "pinch_middle" and event.phase == "start":
                self.mouse_controller.click("right")

            elif event.name == "pinch_ring" and event.phase == "start":
                self.mouse_controller.click("left")
                time.sleep(0.04)
                self.mouse_controller.click("left")

            # 3. Continuous Scrolling
            elif event.name == "peace":
                if now - self._last_scroll_time > 0.07:
                    self._last_scroll_time = now
                    self.mouse_controller.scroll(75)

            elif event.name == "three_fingers":
                if now - self._last_scroll_time > 0.07:
                    self._last_scroll_time = now
                    self.mouse_controller.scroll(-75)

            # 4. Discrete System & Application Shortcuts (Protected by cooldown)
            elif event.phase == "start":
                if now - self._last_discrete_action_time < self.action_cooldown:
                    continue

                if event.name == "four_fingers":
                    self._last_discrete_action_time = now
                    SystemActionController.switch_window()

                elif event.name == "fist":
                    self._last_discrete_action_time = now
                    SystemActionController.show_desktop()

                elif event.name == "thumbs_up":
                    self._last_discrete_action_time = now
                    SystemActionController.launch_browser()

                elif event.name == "rock_horns":
                    self._last_discrete_action_time = now
                    SystemActionController.launch_calculator()

                elif event.name == "pinky_up":
                    self._last_discrete_action_time = now
                    SystemActionController.launch_notepad()

                elif event.name == "call_me":
                    self._last_discrete_action_time = now
                    SystemActionController.launch_file_explorer()

                elif event.name == "gun_l_shape":
                    self._last_discrete_action_time = now
                    SystemActionController.take_screenshot()

                elif event.name == "ok_sign":
                    self._last_discrete_action_time = now
                    SystemActionController.media_play_pause()
