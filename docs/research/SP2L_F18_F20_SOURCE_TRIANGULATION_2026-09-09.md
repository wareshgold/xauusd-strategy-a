# SP2L F18-F20 Source Triangulation — 2026-09-09

## Purpose
Advance source resolution across three blockers in one controlled pass: Trigger (B4), AB=CD anchors/tolerance (B5), and Leg-2 / TP geometry (B6). No historical profitability is used to infer source meaning.

## Primary evidence
- Authoritative SP2L video: `7HEC5mO3d3U`.
- Direct frame inspection around 31:43-35:50, 36:15-37:10, 38:18-40:16 and 53:16-55:25.
- Recovered transcript referenced by the source ledger.

## F18 — Trigger

### Source findings
The source explicitly presents 1-candle, 2-candle and 3-candle trigger constructions, and teaching examples also use a bar/key-bar confirmation concept. The 53:16 passage explicitly describes building one/two/three candles and then placing the pending Limit trigger. The visual sequence around the Entry section also retains the pending-limit mechanism.

### Discrimination result
**CONFIRMED:** trigger is a source concept and a family of observed candle-level constructions.

**NOT FROZEN:** which form is mandatory, how candle acceptance is determined, and the exact timing relation between trigger and pending-order placement.

### Negative result
A market close-reclaim is not an authorized substitute for the source's pending-limit mechanism.

## F19 — AB=CD

### Source findings
The source explicitly displays `AB=CD` and discusses Leg 2 as approximately the same magnitude as Leg 1. This is a magnitude relationship. The source does not uniquely label four OHLC anchor points A/B/C/D.

### Discrimination result
Competing wick, body, structural-pivot and mixed anchor models can all be represented without contradiction to the text alone. Exact equality can be tested synthetically, but the source does not provide a numerical tolerance.

**CONFIRMED:** `Leg2 magnitude =/approximately Leg1 magnitude` as source meaning.

**UNRESOLVED:** A/B/C/D anchor algorithm and tolerance.

No Fibonacci retracement percentage is introduced.

## F20 — Leg 1 / Leg 2 / TP

### Source findings
The source distinguishes first leg and second leg, discusses a pullback toward the start of Leg 2, and separately shows Entry and SL from the later Leg-2/target region. The 55:02 example visually orders `SL → Enter → leg 2`, supporting separation of Entry from Leg-2 start/target region.

The source also explicitly distinguishes TP1 and TP2 and states that the teacher generally uses TP1, while TP2 should be backtested.

### Discrimination result
**CONFIRMED:** Leg 2 is a separate continuation objective and its magnitude is tied to Leg 1 through AB=CD.

**CONFIRMED:** TP1 is the teacher's preferred exit concept in the cited teaching passage; TP2 remains a backtest candidate.

**UNRESOLVED:** exact A/B/C/D projection anchors, exact TP1 price formula, TP2 implementation, and any tolerance/early-exit rule.

## Synthetic fixture result
The combined F18-F20 fixture deliberately retains competing interpretations and verifies only source-safe relationships:

- 1/2/3-candle and key-bar trigger candidates remain representable;
- market reclaim remains negative;
- exact AB=CD magnitude can be discriminated without inventing tolerance;
- wick/body/pivot/mixed anchor models remain explicit alternatives;
- Entry and Leg-2 start can be distinct;
- Leg-2 magnitude projection can be represented as a candidate, not a production TP rule.

## Gate decision
**SYNTHETIC DISCRIMINATION: PASS.**

**SOURCE RESOLUTION: PARTIAL PASS — B4/B5/B6 materially narrowed.**

**FROZEN GEOMETRY: BLOCKED.**

The remaining uncertainty is now concentrated in exact source geometry rather than general strategy semantics:

1. Trigger acceptance/timing.
2. P-Gap OHLC construction.
3. Relevant Low/High and Entry anchor.
4. Structural SL OHLC anchor and wick/body semantics.
5. Pending-order replacement condition.
6. A/B/C/D anchor points and AB=CD tolerance.
7. Exact Leg-2/TP1/TP2 executable geometry.
8. Canonical session filter.

## Research rule
Do not backtest these unresolved alternatives and then select the most profitable one as the source meaning. Historical DEV remains locked until the geometry is frozen.
