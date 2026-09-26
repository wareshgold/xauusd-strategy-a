# SP2L SOURCE RESOLUTION CHECKPOINT — 2026-09-26 — PRESSURE GAP FORMULA UPDATE

Branch: research/sp2l-f13-forensic-repro-2026-09-26

## P-Gap identity

P-Gap = Pressure Gap (گپ فشار). They are the same concept, not two different geometries.

## Source-derived Gap formula

The source material states:

> به فاصله بین سقف ۲ کندل قبل و کف کندل حاضر دقت کنید که اگر فاصله داشت گپ ایجاد شده است.

This gives the executable gap relation:

### Bullish gap
`Low[t] > High[t-2]`

### Bearish gap
The direct source text shown in the recovered material states the bullish orientation. The bearish expression is the mathematical mirror:

`High[t] < Low[t-2]`

The bearish mirror is therefore retained as **source-aligned inference**, not falsely labeled as a verbatim source formula.

## Pressure Gap classification

The same source material defines Pressure Gap as a gap that occurs after approximately 10–30 candles of trend/pressure, when buying pressure temporarily stops and a trend bar then appears, increasing the probability of a trend beginning/continuing.

Therefore the current source-aligned decomposition is:

`GAP(t) = Low[t] > High[t-2]` for bullish, or the mirrored bearish relation.

`P_GAP(t) = GAP(t) + Pressure-Gap contextual classification`

The formula for the geometric gap is now resolved at the source level. What remains unresolved is the fully deterministic encoding of the **pressure context**:
- exact definition of “10–30 candles in trend”
- exact definition of “pressure stops”
- exact trend-bar requirements
- exact mapping of `t` to the SP2L Spike candle
- whether any minimum price-distance threshold is required beyond strict separation.

## Important correction

The old candidate:

`low[1] > high[3] + 1`

is **not** the source formula and remains rejected as canonical.

The source-derived relationship is instead based on:

`Low[current] > High[two-candles-before]`

with the bearish mathematical mirror:

`High[current] < Low[two-candles-before]`.

## Gate

P-GAP = PRESSURE GAP: SOURCE-CONFIRMED
BASE GAP GEOMETRY: SOURCE-DERIVED / RESOLVED
BULLISH GAP RELATION: SOURCE-CONFIRMED
BEARISH GAP RELATION: SOURCE-ALIGNED MIRROR
PRESSURE CONTEXT: PARTIALLY-RESOLVED
SP2L SPIKE INDEX MAPPING: UNRESOLVED
FROZEN SP2L GEOMETRY: BLOCKED
DETECTOR PROMOTION: BLOCKED
PRODUCTION: NOT READY

## Non-negotiable

Do not modify the detector or backtest from this checkpoint until synthetic fixtures verify that the source-derived gap relation is mapped to the correct SP2L candle roles.
