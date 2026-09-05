# Strategy A — Poorsamadi Candidate Rules v1

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Status:** Review-only candidate codification; not implemented

This document converts the strongest source evidence into candidate deterministic rules. It intentionally separates rules that are now sufficiently supported from parameters that remain unresolved.

## 1. Candidate lifecycle

```text
RANGE
  → BREAKOUT
  → IMMEDIATE FT
  → SPIKE FAMILY
  → CORRECTION
  → PENDING LIMIT
  → FILL
  → LEG 2
  → TP1 / EXIT
```

Cancellation/invalidation can occur before fill, and structural SL applies after fill.

## 2. Candidate rules

### C1 — Range prerequisite

A candidate SP2L spike must emerge from a preceding price-action range/context.

**Supported:** yes.

**Still TBD:** exact range detector.

---

### C2 — Breakout

A breakout occurs when the current candle closes beyond the relevant prior structural level.

Bullish:
`close > resistance`

Bearish:
`close < support`

**Supported:** yes.

**Still TBD:** how the relevant structural level is selected.

The existing fixed 5-candle lookback remains a legacy implementation parameter and is not promoted.

---

### C3 — Immediate FT

For the demonstrated SP2L branch, the candle immediately following the breakout is the FT/key bar.

A valid FT must not return into / overlap the relevant prior area in the source-described sense.

**Supported:** strong.

**Still TBD:** exact area and wick/body geometry.

---

### C4 — Spike family

A valid spike belongs to the strong-movement family described by the source. The family can appear through multiple equivalent sequence variants, including:

1. breakout → FT → higher-low/lower-high continuation;
2. higher-low/lower-high structure → P-GAP;
3. short strong structural movement followed by reversal/correction.

These are not separate strategies at v1.

**Supported:** yes.

**Still TBD:** formal grammar and boundaries.

---

### C5 — Directional structure

Bullish strong movement is represented by successive higher lows; bearish movement by successive lower highs.

**Supported:** yes.

**Still TBD:** minimum count and exact swing algorithm.

---

### C6 — Correction

After the strong directional movement, correction begins when price reaches/breaches the first relevant structural low/high of the move.

Bullish:
`price < firstRelevantLow`

Bearish:
`price > firstRelevantHigh`

**Supported:** strong in the demonstrated pattern.

**Still TBD:** exact equality/touch semantics and canonical first-level definition.

---

### C7 — Pending limit order

Once the source-defined correction/order condition occurs, the strategy may place a pending limit order at the source-defined structural level rather than waiting for a future candle close.

**Supported:** yes.

**Still TBD:** exact limit price.

---

### C8 — Fill

The pending order becomes an active position when price reaches the limit level.

**Supported:** source-compatible.

**Still TBD:** intrabar execution convention and same-candle entry/SL/TP ambiguity.

---

### C9 — Structural SL

SL is fixed from the planned structural invalidation level. The trader does not widen the stop simply because price moves adversely.

**Supported:** yes as principle.

**Still TBD:** exact level and execution mechanics.

---

### C10 — Leg 1

Leg 1 is the first directional movement that precedes the correction.

**Supported:** yes.

**Still TBD:** exact numerical endpoints.

Do not use the current `first.open → last.close` formula as canonical.

---

### C11 — Leg 2

After correction, expected Leg 2 magnitude equals Leg 1 magnitude.

Conceptually:

`Leg2Magnitude = Leg1Magnitude`

**Supported:** yes.

**Still TBD:** projection reference and tolerance.

---

### C12 — TP1

TP1 is the preferred exit mode for the demonstrated base strategy. TP2 exists but is described as less suitable in this context.

**Supported:** yes as preference.

**Still TBD:** exact price formula and whether TP1 is mandatory for the base population.

---

### C13 — 2X

A second position can be opened when the first position reaches approximately 50% of its target.

`2X_TRIGGER = 0.5 × distance(entry1, target1)`

**Supported:** strong explicit example.

2X must remain a separate position event with its own entry, SL, risk and outcome.

**Still TBD:** exact second-entry level, SL, eligibility and aggregation.

---

### C14 — Context / location

SP2L is intended to be applied at meaningful locations/context rather than blindly everywhere.

The source explicitly mentions round/trend levels, moving averages/equilibrium, cycles, channels and time-of-day context.

**Supported:** yes as context principle.

**Still TBD:** which contexts are mandatory for Strategy A.

---

## 3. Parameters explicitly NOT promoted

The following remain legacy/research parameters and must not be called source-canonical:

- EMA 60;
- round step 50;
- London 07:00–16:00 UTC;
- New York 13:00–22:00 UTC;
- spike maxCandles 8;
- directional fraction 0.50;
- overlap fraction 0.80;
- breakout lookback 5;
- FT max bars 2;
- close-reclaim entry;
- current Leg 1 `first.open → last.close` formula.

## 4. Implementation gate

No implementation change is authorized solely by this candidate document.

Before coding, the team must resolve the P0 unknowns:

1. structural level;
2. P-GAP geometry;
3. first low/high;
4. Leg 1 endpoints;
5. pending limit price;
6. SL level;
7. execution ordering.

Only then should the deterministic engine be rewritten and backtested from scratch.

## 5. Research separation

Previous DELAY1/T1 MAE research remains unchanged and separate. It is not a source rule and cannot be used to fill any TBD item above.
