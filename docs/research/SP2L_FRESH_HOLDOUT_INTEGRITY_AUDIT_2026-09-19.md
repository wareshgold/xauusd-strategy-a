# SP2L Fresh Holdout — Integrity Audit — 2026-09-19

## Purpose

This audit verifies that the frozen Fresh Holdout path is structurally ready to receive the first eligible post-boundary MT5 data without changing the research protocol.

## Verified runner

File: `scripts/run-author-replica-mt5-fresh-holdout.py`

The committed runner:

- freezes the boundary at **2026-09-19 00:00:00 UTC**;
- uses exactly one configuration:
  - P-Gap = 1.0
  - Spike Multiplier = 1.5
  - Max SL = 10.0
  - TP = 1.0R;
- requests data only from the frozen boundary through the current UTC time;
- uses `MetaTrader5.copy_rates_range`;
- rejects/does not score an empty dataset as a strategy result;
- only admits signals whose trigger timestamp is at or after the frozen boundary;
- does not sweep or tune parameters;
- does not select a favorable post-result subperiod;
- does not change source geometry;
- does not change fill semantics;
- does not promote unresolved AB=CD or Leg1=Leg2 assumptions;
- records WIN / LOSS / AMBIGUOUS / OPEN_OR_UNRESOLVED without converting unresolved trades into decisive results;
- explicitly states that the artifact does not authorize live trading.

## Latest availability check

Latest local execution on 2026-09-19:

- requested start: **2026-09-19 00:00:00 UTC**
- requested end: **2026-09-19 07:37:38 UTC**
- symbol: **XAUUSD.ecn**
- timeframe: **M1**
- returned bars: **0**
- MT5 acquisition error: **null**
- status: **HOLDOUT_DATA_UNAVAILABLE**

This is a data-availability observation, not a Strategy A performance result and not a failed holdout.

## Boundary contamination check

No pre-boundary substitution is permitted. Earlier MT5 acquisition evidence ending at 2026-09-18 23:57 UTC does not qualify for this holdout.

The frozen boundary remains unchanged.

## Production safety check

The Fresh Holdout runner is research-only and does not place trades. The separate Nexora live gateway remains guarded by `LIVE_TRADING_ENABLE=false`.

## Gate disposition

- Frozen boundary: **FROZEN**
- Frozen parameters: **UNCHANGED**
- Holdout integrity path: **READY**
- Eligible post-boundary data: **NOT AVAILABLE YET**
- Untouched Fresh Holdout result: **NOT RUN**
- Parameter tuning: **NONE**
- Geometry reinterpretation: **NONE**
- Production authorization: **BLOCKED**

## Next valid action

After eligible post-boundary `XAUUSD.ecn` M1 data exists, rerun the same committed runner. Do not alter the boundary, parameters, geometry, fill semantics, or subperiod selection rules before observing the holdout result.
