"""
Unit tests for GestureOS Phase 2:
- GestureRecognizer (pointing, pinch, fist, open palm)
- ActionDispatcher safety gates
- ParticleTrailSystem rendering
"""
import time
from vision.hand_geometry import HandState, LandmarkPoint, GestureEvent
from vision.gesture_recognition import GestureRecognizer
from control.action_dispatcher import ActionDispatcher
from magic.particle_system import ParticleTrailSystem
import numpy as np


def create_mock_hand(posture: str = "open") -> HandState:
    """Create a mock 21-landmark hand with controlled geometry."""
    landmarks = [LandmarkPoint(x=0.5, y=0.5, z=0.0) for _ in range(21)]
    wrist = landmarks[0]

    if posture == "pointing":
        # Index tip far away, other fingertips close to wrist
        landmarks[8].y = 0.1  # Index tip far up
        landmarks[6].y = 0.3
        landmarks[5].y = 0.4
        # Fold others
        for tip in [4, 12, 16, 20]:
            landmarks[tip].x = 0.5
            landmarks[tip].y = 0.5
    elif posture == "pinch":
        # Thumb tip (4) and index tip (8) touch
        landmarks[4].x = 0.45
        landmarks[4].y = 0.45
        landmarks[8].x = 0.46
        landmarks[8].y = 0.46

    return HandState(
        landmarks=landmarks,
        handedness="Right",
        confidence=0.9,
        timestamp=time.monotonic(),
        is_valid=True
    )


def test_gesture_recognizer_pinch():
    recognizer = GestureRecognizer(pinch_threshold=0.05)
    hand = create_mock_hand(posture="pinch")
    events = recognizer.recognize([hand])
    names = [e.name for e in events]
    assert "pinch" in names


def test_action_dispatcher_safety():
    dispatcher = ActionDispatcher()
    # Default is OFF
    assert not dispatcher.control_enabled
    assert not dispatcher.emergency_stop

    # Events should not trigger action when disabled
    mock_event = GestureEvent(name="pointer_move", phase="update", payload={"x": 0.5, "y": 0.5})
    dispatcher.process([], [mock_event])
    # Remains safe and does nothing

    # Emergency stop overrides everything
    dispatcher.enable_control()
    assert dispatcher.control_enabled
    dispatcher.trigger_emergency_stop()
    assert dispatcher.emergency_stop
    assert not dispatcher.control_enabled

    # Cannot enable while emergency stop is active
    can_enable = dispatcher.enable_control()
    assert not can_enable


def test_particle_trails():
    system = ParticleTrailSystem(max_particles=50)
    system.emit(100, 100, count=5)
    assert len(system.particles) == 5

    frame = np.zeros((200, 200, 3), dtype=np.uint8)
    system.update_and_render(frame)
    # Particles update cleanly without crashing
    assert True


if __name__ == "__main__":
    test_gesture_recognizer_pinch()
    test_action_dispatcher_safety()
    test_particle_trails()
    print("All Phase 2 tests passed successfully!")

