"""
Unit tests for GestureOS utils and vision data structures.
"""
import time
from utils.performance import FPSCounter
from utils.smoothing import ExponentialSmoother
from vision.hand_geometry import HandState, LandmarkPoint


def test_fps_counter():
    counter = FPSCounter(window_size=5)
    assert counter.fps == 0.0
    for _ in range(5):
        counter.tick()
        time.sleep(0.01)
    assert counter.fps > 0.0


def test_exponential_smoother():
    smoother = ExponentialSmoother(alpha=0.5)
    x1, y1 = smoother.update(100.0, 200.0)
    assert x1 == 100.0 and y1 == 200.0

    # Test that subsequent update smoothly interpolates between points
    x2, y2 = smoother.update(150.0, 250.0)
    assert 100.0 < x2 < 150.0
    assert 200.0 < y2 < 250.0


def test_hand_geometry_properties():
    landmarks = [LandmarkPoint(x=float(i) / 20.0, y=float(i) / 20.0, z=0.0) for i in range(21)]
    hand = HandState(
        landmarks=landmarks,
        handedness="Right",
        confidence=0.95,
        timestamp=time.monotonic(),
        is_valid=True
    )

    assert hand.wrist is not None and hand.wrist.x == 0.0
    assert hand.thumb_tip is not None and abs(hand.thumb_tip.x - 4 / 20.0) < 1e-5
    assert hand.index_tip is not None and abs(hand.index_tip.x - 8 / 20.0) < 1e-5


if __name__ == "__main__":
    test_fps_counter()
    test_exponential_smoother()
    test_hand_geometry_properties()
    print("All basic unit tests passed successfully!")
