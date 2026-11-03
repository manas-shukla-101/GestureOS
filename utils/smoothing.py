"""
Exponential Moving Average and One-Euro stabilization filters for cursor smoothing.
"""
from typing import Tuple, Optional
import math
import time


class ExponentialSmoother:
    """
    Adaptive Exponential Moving Average with dynamic velocity weighting.
    Reduces jitter at low speeds while eliminating lag at high speeds.
    """
    def __init__(self, alpha: float = 0.4):
        self.alpha = max(0.05, min(1.0, alpha))
        self._val: Optional[Tuple[float, float]] = None

    def update(self, x: float, y: float) -> Tuple[float, float]:
        if self._val is None:
            self._val = (x, y)
            return self._val

        prev_x, prev_y = self._val
        dx = x - prev_x
        dy = y - prev_y
        dist = math.hypot(dx, dy)

        # Dynamic smoothing: If moving fast, increase responsiveness (raise alpha)
        # If moving slowly, decrease alpha to eliminate jitter
        speed_factor = min(1.0, dist / 80.0)
        effective_alpha = self.alpha + (1.0 - self.alpha) * (speed_factor ** 2)

        smooth_x = effective_alpha * x + (1.0 - effective_alpha) * prev_x
        smooth_y = effective_alpha * y + (1.0 - effective_alpha) * prev_y
        self._val = (smooth_x, smooth_y)
        return self._val

    def reset(self):
        self._val = None
