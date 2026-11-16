"""Research-only observability wrappers for the SP2L V3.1 signal loop.

This module does not import MT5, initialize a terminal, place orders, or infer
canonical strategy rules. It wraps already-injected rates/finder callables and
emits bounded diagnostic events through a caller-supplied sink.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


EventSink = Callable[[dict[str, Any]], None]


def install_signal_observability(runner: Any, emit: EventSink) -> Callable[[], None]:
    """Wrap runner.rates and runner.find_latest_candidate; return a restore fn.

    Important limits:
    * A None returned by runner.rates is not classified as a terminal/API
      failure versus an upstream insufficient-bars filter.
    * A None returned by the candidate finder is not classified as "no pattern"
      versus a session/time/cutoff filter inside that finder.
    * The wrapper records observations only; it never changes returned values.
    """
    original_rates = runner.rates
    original_finder = runner.find_latest_candidate

    def observed_rates(*args: Any, **kwargs: Any) -> Any:
        symbol = args[0] if args else kwargs.get("symbol")
        try:
            data = original_rates(*args, **kwargs)
        except Exception as exc:
            emit({
                "event": "RATES_ERROR",
                "symbol": symbol,
                "error_type": type(exc).__name__,
                "detail": str(exc),
                "canonical": False,
            })
            raise

        if data is None:
            emit({
                "event": "RATES_UNAVAILABLE",
                "symbol": symbol,
                "reason": "RATES_RETURNED_NONE",
                "interpretation": (
                    "UPSTREAM_CAUSE_UNRESOLVED; may include terminal/API "
                    "failure or an upstream insufficient-bars filter"
                ),
                "canonical": False,
            })
            return data

        try:
            row_count = len(data)
        except Exception:
            row_count = None
        emit({
            "event": "RATES_OK",
            "symbol": symbol,
            "row_count": row_count,
            "canonical": False,
        })
        return data

    def observed_finder(data: Any, symbol: str, *args: Any, **kwargs: Any) -> Any:
        try:
            candidate = original_finder(data, symbol, *args, **kwargs)
        except Exception as exc:
            emit({
                "event": "CANDIDATE_ERROR",
                "symbol": symbol,
                "error_type": type(exc).__name__,
                "detail": str(exc),
                "canonical": False,
            })
            raise

        if candidate is None:
            emit({
                "event": "CANDIDATE_NONE",
                "symbol": symbol,
                "interpretation": (
                    "FINDER_RETURNED_NONE; does not distinguish no pattern "
                    "from a candidate filtered inside the finder"
                ),
                "canonical": False,
            })
        else:
            trigger_time = candidate.get("trigger_time") if hasattr(candidate, "get") else None
            emit({
                "event": "CANDIDATE_FOUND",
                "symbol": symbol,
                "trigger_time": trigger_time,
                "canonical": False,
            })
        return candidate

    runner.rates = observed_rates
    runner.find_latest_candidate = observed_finder

    restored = False

    def restore() -> None:
        nonlocal restored
        if restored:
            return
        runner.rates = original_rates
        runner.find_latest_candidate = original_finder
        restored = True

    return restore
