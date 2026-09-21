# MT5 Session Matrix Next Stage — 2026-09-20

## Status

RESEARCH IN PROGRESS

Branch: `research/sp2l-mt5-session-matrix-2026-09-17-x`

## Existing Evidence Carried Forward

- MT5 acquisition work identified unresolved timestamp basis differences between terminal/server time and UTC assumptions.
- Session availability analysis must not normalize timestamps until the source basis is verified.
- Trading-session gaps must be measured from raw MT5 output first.

## Next Stage Objective

Build a deterministic session matrix from raw MT5 observations without changing candle data semantics.

## Required Outputs

1. Raw session observation table
   - terminal timestamp
   - converted timestamp candidates (clearly marked as candidates only)
   - availability state
   - gap boundaries

2. Session coverage matrix
   - weekday
   - hour block
   - observed M1 availability count
   - missing intervals
   - evidence status

3. Validation gates

- PASS only when timestamp basis is documented and reproducible.
- BLOCKED when timezone/session interpretation requires assumption.
- No Strategy A signal generation should depend on this matrix until the data basis gate is closed.

## Current Gate

`CURRENT_OBSERVATION_NOT_HISTORICALLY_VERIFIED`

Further work must resolve historical coverage and session interpretation before using MT5 data as a production validation source.
