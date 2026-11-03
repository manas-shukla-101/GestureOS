"""
Data contracts for GestureOS hand tracking, gestures, and state.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class LandmarkPoint:
    x: float  # Normalized [0.0, 1.0]
    y: float  # Normalized [0.0, 1.0]
    z: float  # Relative depth
    visibility: float = 1.0
    presence: float = 1.0


@dataclass
class HandState:
    landmarks: List[LandmarkPoint] = field(default_factory=list)
    handedness: str = "Unknown"  # "Left", "Right", or "Unknown"
    confidence: float = 0.0
    timestamp: float = 0.0
    is_valid: bool = False

    @property
    def wrist(self) -> Optional[LandmarkPoint]:
        return self.landmarks[0] if len(self.landmarks) > 0 else None

    @property
    def index_tip(self) -> Optional[LandmarkPoint]:
        return self.landmarks[8] if len(self.landmarks) > 8 else None

    @property
    def thumb_tip(self) -> Optional[LandmarkPoint]:
        return self.landmarks[4] if len(self.landmarks) > 4 else None

    @property
    def middle_tip(self) -> Optional[LandmarkPoint]:
        return self.landmarks[12] if len(self.landmarks) > 12 else None


@dataclass
class GestureEvent:
    name: str
    phase: str  # "start", "update", "end"
    confidence: float = 1.0
    timestamp: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)

