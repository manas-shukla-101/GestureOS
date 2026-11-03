"""
Performance measurement utilities including FPS tracking and frame time averaging.
"""
import time
from collections import deque


class FPSCounter:
    """Calculates smoothed FPS and frame latency over a moving window."""
    def __init__(self, window_size: int = 30):
        self._window_size = window_size
        self._timestamps = deque(maxlen=window_size)
        self._last_time = time.perf_counter()
        self._fps = 0.0

    def tick(self) -> float:
        """Call on each frame. Returns the current estimated FPS."""
        now = time.perf_counter()
        self._timestamps.append(now)
        if len(self._timestamps) > 1:
            duration = self._timestamps[-1] - self._timestamps[0]
            if duration > 0:
                self._fps = (len(self._timestamps) - 1) / duration
        return self._fps

    @property
    def fps(self) -> float:
        return self._fps

    def reset(self):
        self._timestamps.clear()
        self._fps = 0.0

