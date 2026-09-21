# SP2L MT5 Live-vs-Export Reproducibility Audit Contract — 2026-09-21

## Objective
Compare direct `MetaTrader5.copy_rates_from()` acquisition against the committed OTET MT5 export without changing candle semantics or Strategy A geometry.

## Required comparison fields
1. returned bar count;
2. first/last timestamp;
3. OHLC sequence;
4. duplicate/chronology/continuity status;
5. signal count;
6. signal timestamps;
7. outcome accounting;
8. provenance metadata.

## Existing runners
- Direct API: `scripts/run-author-replica-mt5-api.py`
- Export replay: `scripts/run-author-replica-mt5-direct.mjs`
- Interval validation: `scripts/mt5_copy_rates_from_validation.py`

## Important limitation
The direct API comparison requires the user's local MT5 terminal/session. Repository inspection alone cannot truthfully produce a live API result.

Therefore no live-vs-export equivalence claim is made until the local run produces both artifacts from the same requested interval.

## Acceptance
A comparison may be marked reproducible only when:
- requested interval is identical;
- symbol/server/timeframe are identical;
- raw timestamps are retained;
- first/last boundaries are reconciled;
- OHLC sequence matches or every difference is explicitly classified;
- signal timestamp differences are explained;
- no timestamp shift is silently applied.

## Strategy isolation
This audit cannot select P-Gap, F08-F15 geometry, entry, stop, fill, or risk rules.

## Gate
- Export replay contract: PRESENT
- Direct MT5 runner: PRESENT
- Live API equivalence: PENDING LOCAL EXECUTION
- Timestamp basis: UNRESOLVED
- Trading/session use: BLOCKED
- Frozen Geometry: BLOCKED
- Production: DISABLED
