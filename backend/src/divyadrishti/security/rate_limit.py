"""In-memory rate limiter."""

from collections import deque
from time import time
from typing import Deque, Dict


class RateLimitExceeded(Exception):
    """Raised when a client exceeds the rate limit."""

    pass


class InMemoryRateLimiter:
    """Simple sliding-window rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: Dict[str, Deque[float]] = {}

    def allow(self, key: str) -> bool:
        """Return True if the request is within the rate limit."""
        now = time()
        window = self._windows.setdefault(key, deque())

        while window and window[0] < now - self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return False

        window.append(now)
        return True
