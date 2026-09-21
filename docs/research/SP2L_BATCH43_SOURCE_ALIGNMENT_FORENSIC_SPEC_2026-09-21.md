# SP2L Batch43 — Source-Alignment P-Gap Forensic Specification — 2026-09-21

## Purpose

This batch measures whether the research Candidate V1 populations visibly contain the structural concepts explicitly supported by the archived teacher evidence.

It is **descriptive research only**. It does not validate Candidate V1 as canonical P-Gap geometry.

## Source-confirmed structural concepts

The archived source audit supports:

1. **10–30 candles of trend pressure**
2. **A pressure pause / compression**
3. **A trend-bar after the pause**
4. **Continuation context / expectation**

These concepts are source-aligned at the qualitative/structural level.

## Explicitly not source-confirmed

Candidate V1 currently uses:

- pause length = 2 candles
- compression factor = 0.75
- trend-body factor = 1.5

These implementation parameters are **not** treated as teacher-confirmed rules.

The following remain unresolved:

- P-Gap OHLC endpoints
- exact candle indexing
- bullish/bearish mirror
- exact trend-bar definition
- deterministic compression boundary
- gap price threshold/formula
- fill semantics
- execution semantics

## Measurement design

The local script:

\`scripts/research/source-alignment-pgap-forensic.py\`

recomputes Candidate V1 only to partition the MT5 sample into:

- Candidate-only
- Overlap with the existing three-candle imbalance observation
- Imbalance-only

For Candidate V1 events it reports raw descriptive measurements:

- pressure length
- median pressure range
- mean pause range
- pause/pressure range ratio
- median pressure body
- trend-bar body
- trend/pressure body ratio
- directional alignment

No measurement is converted into a new pass/fail threshold.

## Interpretation boundary

A measurement can show what Candidate V1 contains; it cannot establish that the teacher intended the same numerical definition.

No outcome, win rate, profit factor, optimization, or holdout result is used in this source-alignment step.

## Gate status

- Source Resolution: **PARTIAL**
- Frozen Geometry: **BLOCKED**
- P-Gap executable geometry: **UNRESOLVED**
- Fresh Holdout: **BLOCKED**
- Production: **BLOCKED**

## Local execution

After pulling this branch, run:

\`python scripts\\research\\source-alignment-pgap-forensic.py --csv data\\mt5-acquisition\\xauusd_ecn_m1_2026-08-21_2026-09-18.csv\`

The generated JSON must be reviewed and archived before any further interpretation.

No canonical Strategy A or production BUY/SELL logic is changed by this batch.
