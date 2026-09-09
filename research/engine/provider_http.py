"""Strategy-neutral HTTP retry policy for research data acquisition."""
from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_seconds: float = 2.0

    def delay(self, retry_number: int) -> float:
        return self.backoff_seconds * (2 ** (retry_number - 1))


def read_with_retries(
    request: Request,
    *,
    timeout: int = 30,
    policy: RetryPolicy = RetryPolicy(),
    sleep=time.sleep,
    opener=None,
) -> bytes:
    """Read an HTTP response, retrying only provider rate-limit responses."""
    if opener is None:
        opener = urlopen
    for attempt in range(policy.max_retries + 1):
        try:
            with opener(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code != 429 or attempt >= policy.max_retries:
                raise
            sleep(policy.delay(attempt + 1))
    raise RuntimeError("unreachable retry state")
