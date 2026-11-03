"""
Gesture Recognition Engine:
Features mutually-exclusive gesture prioritization and strict pinch gating:
- Clicks/pinches are ONLY evaluated when fingers are open/intentional (NOT during a closed fist).
- In a closed fist (all fingers folded), all pinches and app triggers are suppressed.
- Single dominant gesture reported per frame to prevent string collisions like "Pinch + Thumbs Up + Pointer".
"""
from collections import deque
import time
from typing import List, Optional, Tuple, Dict
from vision.hand_geometry import HandState, GestureEvent, LandmarkPoint
from vision.geometry_utils import (
    get_finger_extension_states, get_pinch_distance
)


class GestureRecognizer:
    def __init__(
        self,
        pinch_threshold: float = 0.28,
        pinch_release_threshold: float = 0.42,
        hold_delay_seconds: float = 0.28,
        temporal_window_size: int = 6
    ):
        self.pinch_threshold = pinch_threshold
        self.pinch_release_threshold = pinch_release_threshold
        self.hold_delay_seconds = hold_delay_seconds

        # Multi-finger pinch state tracking
        self._is_pinching_index: Dict[str, bool] = {}
        self._is_pinching_middle: Dict[str, bool] = {}
        self._is_pinching_ring: Dict[str, bool] = {}

        # Temporal analysis buffers
        self._posture_buffers: Dict[str, deque] = {}
        self._candidate_posture: Dict[str, str] = {}
        self._candidate_start_time: Dict[str, float] = {}
        self._gesture_triggered: Dict[str, bool] = {}

    def set_hold_delay(self, seconds: float):
        self.hold_delay_seconds = max(0.1, min(1.0, seconds))

    def _get_majority_posture(self, hand_id: str) -> str:
        buf = self._posture_buffers.get(hand_id)
        if not buf or len(buf) < 3:
            return "none"
        counts = {}
        for item in buf:
            counts[item] = counts.get(item, 0) + 1
        top_posture, top_count = max(counts.items(), key=lambda x: x[1])
        if top_count >= (len(buf) * 0.55):
            return top_posture
        return "none"

    def recognize(self, hands: List[HandState]) -> List[GestureEvent]:
        events: List[GestureEvent] = []
        now = time.monotonic()

        for hand in hands:
            if not hand.is_valid or len(hand.landmarks) < 21:
                continue

            hand_id = hand.handedness or "Primary"
            lms = hand.landmarks

            if hand_id not in self._posture_buffers:
                self._posture_buffers[hand_id] = deque(maxlen=6)

            # 1. Finger Extension States: (thumb, index, middle, ring, pinky)
            thumb, index, middle, ring, pinky = get_finger_extension_states(lms, hand_id)
            extended_count = sum([thumb, index, middle, ring, pinky])
            is_fist = not index and not middle and not ring and not pinky and not thumb

            # 2. Pinch Detection (STRICTLY MUTUALLY EXCLUSIVE WITH FIST)
            # If all 4 fingers are folded into a fist, do NOT evaluate pinches!
            pinch_active = False
            if not is_fist and (index or middle or ring):
                # Index Pinch -> Left Click
                dist_index = get_pinch_distance(lms, 4, 8)
                was_p_idx = self._is_pinching_index.get(hand_id, False)
                if not was_p_idx and dist_index < self.pinch_threshold:
                    self._is_pinching_index[hand_id] = True
                    pinch_active = True
                    events.append(GestureEvent(
                        name="pinch_index", phase="start", timestamp=now,
                        payload={"distance": dist_index, "hand": hand_id}
                    ))
                elif was_p_idx:
                    if dist_index > self.pinch_release_threshold:
                        self._is_pinching_index[hand_id] = False
                        events.append(GestureEvent(name="pinch_index", phase="end", timestamp=now, payload={"hand": hand_id}))
                    else:
                        pinch_active = True
                        events.append(GestureEvent(name="pinch_index", phase="update", timestamp=now, payload={"hand": hand_id}))

                # Middle Pinch -> Right Click
                dist_middle = get_pinch_distance(lms, 4, 12)
                was_p_mid = self._is_pinching_middle.get(hand_id, False)
                if not was_p_mid and dist_middle < self.pinch_threshold:
                    self._is_pinching_middle[hand_id] = True
                    pinch_active = True
                    events.append(GestureEvent(
                        name="pinch_middle", phase="start", timestamp=now,
                        payload={"distance": dist_middle, "hand": hand_id}
                    ))
                elif was_p_mid:
                    if dist_middle > self.pinch_release_threshold:
                        self._is_pinching_middle[hand_id] = False
                        events.append(GestureEvent(name="pinch_middle", phase="end", timestamp=now, payload={"hand": hand_id}))
                    else:
                        pinch_active = True
                        events.append(GestureEvent(name="pinch_middle", phase="update", timestamp=now, payload={"hand": hand_id}))

                # Ring Pinch -> Double Click
                dist_ring = get_pinch_distance(lms, 4, 16)
                was_p_ring = self._is_pinching_ring.get(hand_id, False)
                if not was_p_ring and dist_ring < self.pinch_threshold:
                    self._is_pinching_ring[hand_id] = True
                    pinch_active = True
                    events.append(GestureEvent(
                        name="pinch_ring", phase="start", timestamp=now,
                        payload={"distance": dist_ring, "hand": hand_id}
                    ))
                elif was_p_ring:
                    if dist_ring > self.pinch_release_threshold:
                        self._is_pinching_ring[hand_id] = False
                        events.append(GestureEvent(name="pinch_ring", phase="end", timestamp=now, payload={"hand": hand_id}))
                    else:
                        pinch_active = True
                        events.append(GestureEvent(name="pinch_ring", phase="update", timestamp=now, payload={"hand": hand_id}))
            else:
                # Hand is a fist or no fingers extended -> release all pinches
                self._is_pinching_index[hand_id] = False
                self._is_pinching_middle[hand_id] = False
                self._is_pinching_ring[hand_id] = False

            # 3. Posture Classification (Prioritized single state)
            raw_posture = "none"

            if is_fist:
                raw_posture = "fist"
            elif pinch_active:
                # If currently pinching, the posture is the pinch action itself
                raw_posture = "pinch_index" if self._is_pinching_index.get(hand_id, False) else "none"
            elif thumb and index and middle and ring and pinky:
                raw_posture = "open_palm"
            elif index and middle and ring and pinky and not thumb:
                raw_posture = "four_fingers"
            elif index and middle and ring and not pinky:
                raw_posture = "three_fingers"
            elif index and middle and not ring and not pinky:
                raw_posture = "peace"
            elif index and not middle and not ring and not pinky and not thumb:
                raw_posture = "pointing"
            elif thumb and not index and not middle and not ring and not pinky:
                raw_posture = "thumbs_up"
            elif index and pinky and not middle and not ring and not thumb:
                raw_posture = "rock_horns"
            elif pinky and not index and not middle and not ring and not thumb:
                raw_posture = "pinky_up"
            elif thumb and pinky and not index and not middle and not ring:
                raw_posture = "call_me"
            elif thumb and index and not middle and not ring and not pinky:
                raw_posture = "gun_l_shape"

            # 4. Continuous cursor tracking (ONLY when index finger is deliberately pointing or active pinch)
            if (raw_posture == "pointing" or pinch_active) and hand.index_tip:
                events.append(GestureEvent(
                    name="pointer_move",
                    phase="update",
                    confidence=hand.confidence,
                    timestamp=now,
                    payload={"x": hand.index_tip.x, "y": hand.index_tip.y, "hand": hand_id}
                ))

            # 5. Temporal Filtering & Intentional Hold Delay Verification
            self._posture_buffers[hand_id].append(raw_posture)
            voted_posture = self._get_majority_posture(hand_id)

            curr_candidate = self._candidate_posture.get(hand_id, "none")

            if voted_posture != curr_candidate:
                self._candidate_posture[hand_id] = voted_posture
                self._candidate_start_time[hand_id] = now
                self._gesture_triggered[hand_id] = False
            else:
                candidate_start = self._candidate_start_time.get(hand_id, now)
                hold_elapsed = now - candidate_start

                # Scrolling gestures activate faster (0.12s)
                # Discrete shortcuts require user hold_delay (0.28s)
                required_delay = 0.12 if voted_posture in ("peace", "three_fingers") else self.hold_delay_seconds

                if voted_posture != "none" and hold_elapsed >= required_delay:
                    already_triggered = self._gesture_triggered.get(hand_id, False)

                    if not already_triggered:
                        self._gesture_triggered[hand_id] = True
                        events.append(GestureEvent(
                            name=voted_posture,
                            phase="start",
                            timestamp=now,
                            payload={"hand": hand_id, "hold_duration": hold_elapsed}
                        ))
                    else:
                        events.append(GestureEvent(
                            name=voted_posture,
                            phase="update",
                            timestamp=now,
                            payload={"hand": hand_id, "hold_duration": hold_elapsed}
                        ))

        return events
