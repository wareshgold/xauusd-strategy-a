# SP2L V3.1 Signal-Loop Observability — Research Only
Date: 2026-11-16

## Purpose
Provide a small, injectable observer for the two silent branches identified in
the V3.1 loop: rates retrieval and candidate detection. This is a research
instrumentation component, not a runner, strategy change, or execution change.

## Safety boundary
- No MetaTrader5 import or terminal initialization.
- No broker/account access, orders, cancellations, or position changes.
- No filesystem writes.
- No canonical rule, signal, BUY/SELL decision, or geometry interpretation.
- The caller supplies an existing runner-like object and an event sink.
- The wrapper preserves the exact values returned by the wrapped functions.
- A restore callback returns both wrapped functions to their original objects.

## Events
- `RATES_OK`: the wrapped rates function returned a non-None object; records
  its row count when available.
- `RATES_UNAVAILABLE`: the wrapped rates function returned None.
- `RATES_ERROR`: the wrapped rates function raised; the exception is re-raised.
- `CANDIDATE_NONE`: the wrapped finder returned None.
- `CANDIDATE_FOUND`: the wrapped finder returned a candidate; records its
  trigger_time when available.
- `CANDIDATE_ERROR`: the wrapped finder raised; the exception is re-raised.

## Explicit unresolved distinctions
The existing base `rates()` function collapses an MT5 None response and fewer
than six bars into the same None result. This wrapper cannot separate those
causes and labels them unresolved. Separating them requires instrumentation
inside the underlying rates function around `copy_rates_from_pos`.

Likewise, `CANDIDATE_NONE` does not prove that no SP2L pattern existed. The
V3.1 session wrapper may return None because the original finder found no
candidate or because a candidate was rejected by its trigger-time cutoff.
Separate events require observation inside that wrapper before and after the
cutoff comparison.

## Deployment boundary
This module is not attached to the currently running V3.1 process and does not
observe it retroactively. It must not be loaded into a second MT5 process.
Any future integration must occur only in a separately approved, controlled
runner revision and restart window, after review of the exact instrumentation
points. Until then, the active runner remains untouched.

## Validation
Eight synthetic unit tests cover event classification, return-value
preservation, exception propagation, and idempotent restoration. Tests are
authored but have not yet been executed in the user's local environment.
