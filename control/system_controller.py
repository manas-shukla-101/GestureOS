"""
Windows System, Keyboard, Multimedia, and Application Controller:
Handles comprehensive hands-free OS control via direct Win32 API calls:
- Window Management (Alt+Tab switch, Minimize All / Win+D, Task View / Win+Tab, Close Window / Alt+F4)
- Multimedia (Play/Pause, Next Track, Prev Track, Volume Mute/Up/Down)
- System Actions (Screenshot / Win+Shift+S, Lock Screen / Win+L)
- Application Launchers (Browser, Calculator, Notepad, File Explorer, Task Manager, Terminal)
"""
import os
import subprocess
import ctypes
import time
from utils.logging_config import logger

user32 = ctypes.windll.user32

# Virtual key constants
VK_LWIN = 0x5B
VK_TAB = 0x09
VK_MENU = 0x12     # Alt
VK_SHIFT = 0x10    # Shift
VK_CONTROL = 0x11  # Ctrl
VK_ESCAPE = 0x1B
VK_RETURN = 0x0D
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_F4 = 0x73

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

KEYEVENTF_KEYUP = 0x0002


def key_down(vk_code: int):
    user32.keybd_event(vk_code, 0, 0, 0)


def key_up(vk_code: int):
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def send_key(vk_code: int):
    key_down(vk_code)
    time.sleep(0.01)
    key_up(vk_code)


def send_combo(*vk_codes: int):
    """Presses keys in sequence, holds them, and releases in reverse order."""
    for vk in vk_codes:
        key_down(vk)
        time.sleep(0.01)
    time.sleep(0.02)
    for vk in reversed(vk_codes):
        key_up(vk)
        time.sleep(0.01)


class SystemActionController:
    # --- Applications ---
    @staticmethod
    def launch_browser():
        logger.info("Gesture Action: Open Web Browser")
        os.system("start https://www.google.com")

    @staticmethod
    def launch_calculator():
        logger.info("Gesture Action: Open Calculator")
        subprocess.Popen("calc.exe")

    @staticmethod
    def launch_notepad():
        logger.info("Gesture Action: Open Notepad")
        subprocess.Popen("notepad.exe")

    @staticmethod
    def launch_file_explorer():
        logger.info("Gesture Action: Open File Explorer")
        subprocess.Popen("explorer.exe")

    @staticmethod
    def launch_task_manager():
        logger.info("Gesture Action: Open Task Manager")
        send_combo(VK_CONTROL, VK_SHIFT, VK_ESCAPE)

    @staticmethod
    def launch_terminal():
        logger.info("Gesture Action: Open Terminal / PowerShell")
        subprocess.Popen("powershell.exe")

    # --- Window Management & Navigation ---
    @staticmethod
    def show_desktop():
        """Win + D (Toggle Show/Hide Desktop)"""
        logger.info("Gesture Action: Show Desktop (Win + D)")
        send_combo(VK_LWIN, 0x44)  # 'D'

    @staticmethod
    def switch_window():
        """Alt + Tab (Switch active window)"""
        logger.info("Gesture Action: Switch Window (Alt + Tab)")
        send_combo(VK_MENU, VK_TAB)

    @staticmethod
    def task_view():
        """Win + Tab (Task View / Desktops)"""
        logger.info("Gesture Action: Task View (Win + Tab)")
        send_combo(VK_LWIN, VK_TAB)

    @staticmethod
    def take_screenshot():
        """Win + Shift + S (Snipping tool screenshot)"""
        logger.info("Gesture Action: Screenshot (Win + Shift + S)")
        send_combo(VK_LWIN, VK_SHIFT, 0x53)  # 'S'

    # --- Media & Sound ---
    @staticmethod
    def volume_up():
        logger.info("Gesture Action: Volume UP")
        send_key(VK_VOLUME_UP)

    @staticmethod
    def volume_down():
        logger.info("Gesture Action: Volume DOWN")
        send_key(VK_VOLUME_DOWN)

    @staticmethod
    def volume_mute():
        logger.info("Gesture Action: Toggle Mute")
        send_key(VK_VOLUME_MUTE)

    @staticmethod
    def media_play_pause():
        logger.info("Gesture Action: Media Play / Pause")
        send_key(VK_MEDIA_PLAY_PAUSE)

    @staticmethod
    def media_next():
        logger.info("Gesture Action: Next Track")
        send_key(VK_MEDIA_NEXT_TRACK)
