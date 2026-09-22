# SP2L Exit Management Sensitivity — Research Candidate — 2026-09-22

## Status

Research-only. This experiment does **not** freeze or promote any execution rule to canonical Strategy A.

## Fixed baseline

- Symbol: XAUUSD.ecn
- Timeframe: M1
- P-Gap research candidate: 1.0 price
- Spike multiplier: 1.5
- Maximum SL distance: 10.0 price
- Snapshot set: same six windows used by the RR sensitivity
- TP grid: 0.75R, 1R, 1.25R, 1.5R, 2R
- Base SL candidate: BUY spike/base low, SELL spike/base high
- Intrabar conflict: if active SL and TP are both touched in one candle, outcome is AMBIGUOUS

## Exit-management candidates

1. NO_MANAGEMENT
   - Fixed initial SL and fixed TP.

2. BREAKEVEN_1R
   - After a completed candle reaches +1R, move SL to entry.
   - The new SL becomes active from the following candle.

3. TRAIL_PREV_BAR_1R
   - After +1R activation, trail the SL using the most recently completed candle extreme.
   - BUY: previous completed candle low, only ratcheting upward.
   - SELL: previous completed candle high, only ratcheting downward.
   - Stop updates become active from the following candle.

These management rules are engineering hypotheses only. They are not source-confirmed teacher instructions.

## Interpretation guard

Performance may be compared descriptively, but no result from this experiment can resolve source geometry or promote a production execution rule. Source resolution remains the controlling gate.

## Execution

Run:

    $env:PGAP_PRICE="1"
    python scripts\\run-author-replica-mt5-exit-management-sensitivity.py

The generated JSON artifact is:

    artifacts/author-replica-mt5-exit-management-sensitivity.json
