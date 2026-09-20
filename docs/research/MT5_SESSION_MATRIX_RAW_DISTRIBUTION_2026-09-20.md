# MT5 Raw Session Distribution Matrix 2026-09-20

## Status

SESSION_MATRIX_STATUS: PARTIAL

TIME_ALIGNMENT: UNRESOLVED

TRADING_USE: BLOCKED

## Scope

This artifact records the next analysis layer for MT5 XAUUSD raw timestamp observations.

No timezone conversion, DST adjustment, or broker session assumption is applied.

## Dimensions

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Source: MT5 raw acquisition artifacts
- Timestamp basis: terminal returned timestamps

## Matrix preparation

The matrix tracks:

- weekday distribution
- raw hour distribution
- observed M1 availability
- missing interval inventory
- confidence state

## Gate

Until MT5 server time to UTC alignment is independently verified, this matrix remains an observation artifact only and cannot modify Strategy A execution rules.
