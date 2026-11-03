"""
Robust geometric calculations and 3D angle/vector heuristics for finger extension and posture detection.
"""
import math
from typing import List, Tuple
from vision.hand_geometry import LandmarkPoint, HandState


def euclidean_distance_2d(p1: LandmarkPoint, p2: LandmarkPoint) -> float:
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def euclidean_distance_3d(p1: LandmarkPoint, p2: LandmarkPoint) -> float:
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)


def get_hand_scale(landmarks: List[LandmarkPoint]) -> float:
    """Reference palm scale: distance between wrist (0) and middle MCP (9)."""
    if len(landmarks) < 10:
        return 0.25
    dist = euclidean_distance_2d(landmarks[0], landmarks[9])
    return max(0.08, dist)


def is_finger_extended(landmarks: List[LandmarkPoint], tip_idx: int, pip_idx: int, mcp_idx: int) -> bool:
    """
    Determines if a finger is extended using both distance-from-wrist and PIP-to-tip vector:
    1. Distance of fingertip to wrist must be greater than PIP and MCP distance from wrist.
    2. Fingertip must NOT be folded back towards the palm/MCP.
    """
    if len(landmarks) <= tip_idx:
        return False
    wrist = landmarks[0]
    mcp = landmarks[mcp_idx]
    pip = landmarks[pip_idx]
    tip = landmarks[tip_idx]
    scale = get_hand_scale(landmarks)

    dist_tip_wrist = euclidean_distance_2d(tip, wrist)
    dist_pip_wrist = euclidean_distance_2d(pip, wrist)
    dist_mcp_wrist = euclidean_distance_2d(mcp, wrist)
    dist_tip_mcp = euclidean_distance_2d(tip, mcp)
    dist_pip_mcp = euclidean_distance_2d(pip, mcp)

    # In a fist or folded finger, the tip curves back towards MCP and wrist
    # An extended finger must have tip clearly farther from wrist than PIP/MCP,
    # and tip-to-MCP distance must exceed the PIP-to-MCP segment length
    is_farther_than_pip = dist_tip_wrist > (dist_pip_wrist + 0.08 * scale)
    is_farther_than_mcp = dist_tip_wrist > (dist_mcp_wrist + 0.15 * scale)
    is_straight = dist_tip_mcp > (dist_pip_mcp * 1.25)

    return is_farther_than_pip and is_farther_than_mcp and is_straight


def is_thumb_extended(landmarks: List[LandmarkPoint], handedness: str = "Right") -> bool:
    """
    Thumb extension heuristic:
    1. Thumb tip (4) must be far from index MCP (5) and pinky MCP (17).
    2. When tucked into a fist, thumb tip is close to index MCP (5) or middle MCP (9).
    """
    if len(landmarks) < 21:
        return False
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]
    scale = get_hand_scale(landmarks)

    # Distance from index base and middle base
    dist_to_index_base = euclidean_distance_2d(thumb_tip, index_mcp)
    dist_to_middle_base = euclidean_distance_2d(thumb_tip, middle_mcp)
    dist_tip_mcp = euclidean_distance_2d(thumb_tip, thumb_mcp)

    # If folded across fingers/fist, distance to index/middle base is very small (< 0.45 * scale)
    if dist_to_index_base < (0.42 * scale) or dist_to_middle_base < (0.42 * scale):
        return False

    # For an extended thumb (like Thumbs Up), thumb tip must be well away from index MCP
    return dist_to_index_base > (0.50 * scale) and dist_tip_mcp > (0.40 * scale)


def get_finger_extension_states(landmarks: List[LandmarkPoint], handedness: str = "Right") -> Tuple[bool, bool, bool, bool, bool]:
    """Returns (thumb, index, middle, ring, pinky) extension boolean flags."""
    if len(landmarks) < 21:
        return (False, False, False, False, False)

    thumb = is_thumb_extended(landmarks, handedness)
    index = is_finger_extended(landmarks, tip_idx=8, pip_idx=6, mcp_idx=5)
    middle = is_finger_extended(landmarks, tip_idx=12, pip_idx=10, mcp_idx=9)
    ring = is_finger_extended(landmarks, tip_idx=16, pip_idx=14, mcp_idx=13)
    pinky = is_finger_extended(landmarks, tip_idx=20, pip_idx=18, mcp_idx=17)

    return (thumb, index, middle, ring, pinky)


def get_pinch_distance(landmarks: List[LandmarkPoint], tip1_idx: int = 4, tip2_idx: int = 8) -> float:
    """Normalized pinch distance scaled by reference hand size."""
    if len(landmarks) <= max(tip1_idx, tip2_idx):
        return 1.0
    scale = get_hand_scale(landmarks)
    raw_dist = euclidean_distance_2d(landmarks[tip1_idx], landmarks[tip2_idx])
    return raw_dist / scale
