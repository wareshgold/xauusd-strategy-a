# SP2L Leg 1 / Entry / SL Alignment — 2026-09-08

## Purpose

This note advances source resolution for the relationship between:

`Spike → Leg 1 → Correction → Pending Limit → Structural Invalidation → Leg 2`

It is research-only. No production rule is frozen here.

## Source evidence

### 1. Entry semantics

The source explicitly describes the correction as price moving below the relevant first low in the bullish case and says the order can be placed manually or as a pre-set limit during that correction. The bearish case is the mirrored high condition.

The visual sequence around the entry/SL diagram shows a horizontal `Entry` line placed at the corrective structural level, with a separate `SL` line below the spike-origin structure.

**Status:** STRONG SOURCE EVIDENCE for pending-limit execution during correction.

### 2. Exact entry anchor

The strongest current candidate is:

- BUY: pending limit at the relevant prior candle Low reached by the correction.
- SELL: pending limit at the relevant prior candle High reached by the correction.

This is consistent with the source wording and official strategy description, but the exact definition of “relevant/prior candle” across all spike variants is not yet proven to be identical.

**Status:** STRONG CANDIDATE, not frozen.

### 3. Structural invalidation / SL

The source describes the stop as being known before activation and the scenario becoming invalid if price returns to the invalidation area. The diagram shows SL below the spike-origin structure for BUY and the mirrored placement is expected for SELL.

What remains unresolved is the exact executable price anchor:

- exact first-candle Low/High;
- exact spike-origin candle Low/High;
- structural level derived from more than one candle;
- buffer/tick treatment.

No buffer, tolerance, or wick/body convention is invented here.

**Status:** STRUCTURAL SEMANTICS CONFIRMED; EXACT PRICE ANCHOR UNRESOLVED.

### 4. Leg 1

The source repeatedly describes the second leg as continuing after correction with approximately the same magnitude as the first leg and explicitly names the relationship `AB=CD`.

The strongest current measurement candidate is the directional movement from the source-defined spike origin to the source-defined spike extreme. However, the source does not provide enough evidence to prove that the origin must be the first candle Low/High, breakout level, or another candle-level endpoint for every spike construction.

**Status:** EQUAL-LEG CONCEPT CONFIRMED; EXACT LEG-1 ANCHORS UNRESOLVED.

## Combined candidate model

For research purposes only:

`source-defined spike`
→ `source-defined first-leg movement`
→ `correction reaches relevant prior candle extreme`
→ `pending limit is placed at that structural correction level`
→ `structural invalidation remains beyond spike-origin structure`
→ `second leg projects approximately one first-leg magnitude`

This combined model is compatible with the source without importing classical harmonic A/B/C/D geometry.

## Critical non-assumptions

The following remain explicitly forbidden from canonical implementation:

1. Entry price = classical harmonic C.
2. Entry price = arbitrary 50% retracement.
3. SL = fixed number of points.
4. SL = always exactly the first candle wick.
5. Leg 1 = any generic swing-high/swing-low algorithm.
6. AB=CD tolerance chosen from backtest performance.
7. Market close-reclaim replacing the pending-limit order.

## Synthetic discrimination fixtures

### LEG-ENTRY-01
Prior candle Low/High equals the intended pending-limit price.

Expected research interpretation: supports the prior-candle-extreme candidate.

### LEG-ENTRY-02
Correction reaches the prior candle extreme, but a hypothetical C-point lies elsewhere.

Expected: distinguishes source candle-level entry from classical C-point import.

### LEG-SL-01
Two candidate SL anchors exist: spike-origin wick and preceding structural wick.

Expected: remains unresolved unless source evidence discriminates them.

### LEG-SL-02
Price crosses the candidate invalidation intrabar and closes back inside.

Expected: tests whether invalidation is touch-based or close-based; source currently does not freeze this.

### LEG-01
Spike-origin-to-spike-extreme magnitude differs from breakout-candle-to-extreme magnitude.

Expected: prevents silent selection of a Leg-1 anchor by backtest performance.

### LEG-02
Same visual spike with a deeper correction but unchanged source-defined first-leg magnitude.

Expected: verifies that Leg 2 is measured from the source-defined correction/entry geometry rather than an invented retracement ratio.

## Gate status

- SOURCE RESOLUTION: advanced.
- SYNTHETIC FIXTURES: expanded.
- FROZEN GEOMETRY: **BLOCKED**.
- DEV: locked for canonical Strategy A.
- VAL / HOLDOUT: locked.
- PRODUCTION: unchanged.

## Next blocker

The highest-value unresolved item remains the exact P-Gap boundary/timing. In parallel, the exact SL anchor and Leg-1 origin should remain explicit research variables until direct source evidence discriminates them.
