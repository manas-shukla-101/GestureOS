import os
import urllib.request
from utils.logging_config import logger

MODEL_DIR = "models"
MODEL_NAME = "hand_landmarker.task"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"


def ensure_model_downloaded() -> str:
    """Checks if MediaPipe hand_landmarker model exists; if not, automatically downloads it."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 1000000:
        logger.info(f"Downloading MediaPipe HandLandmarker model to {MODEL_PATH}...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            logger.info("Model download complete.")
        except Exception as e:
            logger.error(f"Failed to download model from {MODEL_URL}: {e}")
            raise e
    return MODEL_PATH

