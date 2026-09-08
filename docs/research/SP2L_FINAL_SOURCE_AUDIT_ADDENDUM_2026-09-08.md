# SP2L Final Source Audit Addendum — Leg-1 / AB=CD — 2026-09-08

This addendum extends `SP2L_FINAL_SOURCE_AUDIT_2026-09-08.md` without changing its gate decision.

## New evidence review
The source AB=CD frames and real-trade chart frames were reviewed specifically for a repeatable Leg-1 anchor. The source clearly establishes the equal-leg relationship and the candle-level character of its AB=CD method, but the drawings do not expose unambiguous A/B/C/D OHLC anchors.

## Source-safe result
`Leg 2 magnitude ≈ Leg 1 magnitude` is confirmed semantically.

No universal executable formula was established for:
- Leg-1 start anchor;
- Leg-1 end anchor;
- projection origin after correction;
- wick/body convention;
- A/B/C/D candle identity;
- numerical AB=CD tolerance.

The classical harmonic/Fibonacci A/B/C interpretation is explicitly kept outside the canonical rule because the source distinguishes its candle-level approach from classical internet AB=CD treatment.

## Gate decision
SOURCE RESOLUTION: semantic contract remains complete.
FROZEN GEOMETRY: **BLOCKED**.
DEV: LOCKED.
VALIDATION: LOCKED and untouched.
FRESH HOLDOUT: LOCKED and untouched.
PRODUCTION: unchanged.

No production implementation or historical parameter was changed as a result of this review.
