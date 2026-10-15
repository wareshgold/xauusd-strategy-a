"""Rate-limited diagnostics for otherwise silent forward-runner polling paths."""

from __future__ import annotations

import time


class ForwardDiagnosticGate:
    """Allow one diagnostic per key per interval; no trading-state side effects."""

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._last_logged: dict[str, float] = {}

    def should_log(self, key: str, interval_seconds: float = 60.0) -> bool:
        now = float(self._clock())
        previous = self._last_logged.get(key)
        if previous is not None and now - previous < float(interval_seconds):
            return False
        self._last_logged[key] = now
        return True
