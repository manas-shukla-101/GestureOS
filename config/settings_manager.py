"""
Local settings persistence manager for GestureOS.
Saves and loads user preferences from config/settings.json.
"""
import json
import os
from typing import Dict, Any
from utils.logging_config import logger

CONFIG_DIR = "config"
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "camera": {
        "index": 0,
        "width": 1280,
        "height": 720,
        "fps": 30,
        "mirror": True,
        "show_landmarks": True
    },
    "control": {
        "smoothing_alpha": 0.35,
        "sensitivity": 1.3,
        "scroll_speed": 60,
        "pinch_threshold": 0.05
    },
    "magic": {
        "active_effect": "none",
        "particle_count": 120,
        "orb_scale": 1.0
    }
}


class SettingsManager:
    def __init__(self, file_path: str = SETTINGS_FILE):
        self.file_path = file_path
        self.settings: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        """Loads settings from JSON or falls back to defaults safely."""
        if not os.path.exists(self.file_path):
            self.save(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge loaded keys over defaults
                merged = DEFAULT_SETTINGS.copy()
                for section, vals in data.items():
                    if section in merged and isinstance(vals, dict):
                        merged[section].update(vals)
                    else:
                        merged[section] = vals
                return merged
        except Exception as e:
            logger.error(f"Error loading settings file: {e}. Falling back to default settings.")
            return DEFAULT_SETTINGS.copy()

    def save(self, data: Dict[str, Any] = None) -> bool:
        """Saves current settings dictionary to disk."""
        if data is not None:
            self.settings = data

        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"Settings saved to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.settings.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any):
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()

