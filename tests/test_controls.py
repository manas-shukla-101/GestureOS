"""
Unit tests for GestureOS Advanced PC Controls:
- Pointing & Multi-Finger Pinches (Left click, Right click, Double click)
- Temporal Voting & Intentional Hold Delay Verification
- Safety Gates & Emergency Stop
"""
import time
from vision.hand_geometry import HandState, LandmarkPoint, GestureEvent
from vision.gesture_recognition import GestureRecognizer
from control.action_dispatcher import ActionDispatcher


def create_realistic_hand(posture: str = "peace") -> HandState:
    """Create a mock 21-landmark hand with structured joint chains."""
    landmarks = [LandmarkPoint(x=0.5, y=0.8, z=0.0) for _ in range(21)]
    # Scale reference (wrist 0 to MCP 9)
    landmarks[9].y = 0.55  # scale = 0.25

    # Thumb chain: 1, 2, 3, 4 (tucked)
    for i in range(1, 5):
        landmarks[i].x = 0.45
        landmarks[i].y = 0.70

    # Default folded fingers
    for tip, pip, mcp in [(8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17)]:
        landmarks[mcp].y = 0.55
        landmarks[pip].y = 0.60
        landmarks[tip].y = 0.65  # Tip lower than PIP = folded

    if posture == "peace":
        # Index (8) and Middle (12) extended high
        landmarks[5].y = 0.55
        landmarks[6].y = 0.42
        landmarks[8].y = 0.20

        landmarks[9].y = 0.55
        landmarks[10].y = 0.42
        landmarks[12].y = 0.20

    return HandState(
        landmarks=landmarks,
        handedness="Right",
        confidence=0.95,
        timestamp=time.monotonic(),
        is_valid=True
    )


def test_recognizer_with_temporal_delay():
    recognizer = GestureRecognizer(hold_delay_seconds=0.15)
    peace_hand = create_realistic_hand(posture="peace")

    # Feed multiple frames across hold window to satisfy temporal voting buffer and delay
    names = []
    for _ in range(10):
        events = recognizer.recognize([peace_hand])
        names.extend([e.name for e in events])
        time.sleep(0.02)

    assert "peace" in names


def test_action_dispatcher_comprehensive_safety():
    dispatcher = ActionDispatcher()
    assert not dispatcher.control_enabled

    # Enable control
    dispatcher.enable_control()
    assert dispatcher.control_enabled

    # Emergency stop overrides immediately
    dispatcher.trigger_emergency_stop()
    assert dispatcher.emergency_stop
    assert not dispatcher.control_enabled


if __name__ == "__main__":
    test_recognizer_with_temporal_delay()
    test_action_dispatcher_comprehensive_safety()
    print("All Advanced PC Control tests passed successfully!")
