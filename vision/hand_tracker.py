"""
Hand tracker encapsulating the MediaPipe Tasks HandLandmarker API.
"""
import os
import time
from typing import List, Tuple
import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from vision.hand_geometry import HandState, LandmarkPoint
from utils.logging_config import logger


# 21 standard Hand landmark connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]


class HandTracker:
    def __init__(self, model_path: str = "models/hand_landmarker.task", num_hands: int = 2):
        self.model_path = model_path
        self.num_hands = num_hands
        self.detector = None
        self._init_detector()

    def _init_detector(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"MediaPipe hand model not found at {self.model_path}")

        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        logger.info(f"HandTracker initialized with model {self.model_path}")

    def process_frame(self, frame_bgr: np.ndarray) -> List[HandState]:
        """
        Process a BGR frame and return detected HandState objects.
        """
        if self.detector is None or frame_bgr is None:
            return []

        # Convert OpenCV BGR to RGB
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        now = time.monotonic()
        detection_result = self.detector.detect(mp_image)

        hands: List[HandState] = []
        if not detection_result.hand_landmarks:
            return hands

        for idx, landmarks in enumerate(detection_result.hand_landmarks):
            handedness_label = "Unknown"
            score = 1.0
            if detection_result.handedness and idx < len(detection_result.handedness):
                categories = detection_result.handedness[idx]
                if categories:
                    handedness_label = categories[0].category_name
                    score = categories[0].score

            landmark_points = [
                LandmarkPoint(
                    x=lm.x,
                    y=lm.y,
                    z=lm.z,
                    visibility=lm.visibility if hasattr(lm, 'visibility') else 1.0,
                    presence=lm.presence if hasattr(lm, 'presence') else 1.0
                )
                for lm in landmarks
            ]

            hands.append(
                HandState(
                    landmarks=landmark_points,
                    handedness=handedness_label,
                    confidence=score,
                    timestamp=now,
                    is_valid=True
                )
            )

        return hands

    @staticmethod
    def draw_landmarks(frame: np.ndarray, hands: List[HandState], color_primary=(53, 217, 255), color_joint=(240, 240, 240)) -> np.ndarray:
        """
        Draw clean, styled landmark overlays matching the futuristic theme.
        """
        h, w, _ = frame.shape
        for hand in hands:
            if not hand.is_valid:
                continue

            # Draw bones/connections
            for start_idx, end_idx in HAND_CONNECTIONS:
                if start_idx < len(hand.landmarks) and end_idx < len(hand.landmarks):
                    p1 = hand.landmarks[start_idx]
                    p2 = hand.landmarks[end_idx]
                    x1, y1 = int(p1.x * w), int(p1.y * h)
                    x2, y2 = int(p2.x * w), int(p2.y * h)
                    cv2.line(frame, (x1, y1), (x2, y2), (40, 40, 50), 3, cv2.LINE_AA)
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 217, 53), 1, cv2.LINE_AA) # Cyan in BGR

            # Draw joint nodes
            for idx, lm in enumerate(hand.landmarks):
                cx, cy = int(lm.x * w), int(lm.y * h)
                # Outer glow ring
                if idx in [4, 8, 12, 16, 20]:  # Fingertips
                    cv2.circle(frame, (cx, cy), 6, (246, 92, 139), -1, cv2.LINE_AA) # Violet in BGR
                    cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1, cv2.LINE_AA)
                else:
                    cv2.circle(frame, (cx, cy), 3, (255, 217, 53), -1, cv2.LINE_AA)

        return frame

