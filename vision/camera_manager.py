"""
Camera Manager: handles video capture hardware enumeration, lifecycle, and frame retrieval.
"""
import time
from typing import List, Optional, Tuple
import cv2
import numpy as np

from utils.logging_config import logger


class CameraManager:
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30):
        self.camera_index = camera_index
        self.target_width = width
        self.target_height = height
        self.target_fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False

    @staticmethod
    def enumerate_cameras(max_tested: int = 4) -> List[int]:
        """Check available camera indices."""
        available = []
        for idx in range(max_tested):
            temp_cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if temp_cap.isOpened():
                available.append(idx)
                temp_cap.release()
        return available if available else [0]

    def open(self, camera_index: Optional[int] = None) -> bool:
        if camera_index is not None:
            self.camera_index = camera_index

        self.release()
        logger.info(f"Opening camera index {self.camera_index} (width={self.target_width}, height={self.target_height})...")
        
        # On Windows, cv2.CAP_DSHOW provides fast startup and stable resolution negotiation
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            # Fallback to default backend
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            logger.warning(f"Could not open camera {self.camera_index}.")
            self.is_opened = False
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        self.is_opened = True
        logger.info(f"Camera {self.camera_index} successfully opened.")
        return True

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.is_opened or self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None
        return True, frame

    def release(self):
        if self.cap is not None:
            logger.info("Releasing camera capture resources...")
            try:
                self.cap.release()
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            self.cap = None
        self.is_opened = False

