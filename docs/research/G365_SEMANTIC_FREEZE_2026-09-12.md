# G365 — SP2L Non-Production Semantic Freeze

**Date:** 2026-09-12  
**Gate:** SOURCE RESOLUTION → semantic freeze only  
**Status:** NON-PRODUCTION / NOT FROZEN GEOMETRY

## Purpose

Freeze only meanings directly supported by the current authoritative source set. This document deliberately does **not** define executable OHLC formulas, numeric tolerances, order prices, or production signal rules.

## Source-confirmed semantics

1. **SP2L identity:** Spike → 2 Leg / AB=CD; the lesson uses SP2L as a name for this framework.
2. **Valid Spike / P-Gap:** a valid breakout/spike is associated with P-Gap; the gap lesson establishes P-Gap as Pressure Gap (`گپ فشار`).
3. **Gap taxonomy:** Breakout Gap, Pressure Gap, Exhaustion Gap, and Common Gap are distinct source categories. Category depends on context/location, not merely the existence of visual separation.
4. **Pressure Gap context:** sustained directional pressure, a temporary pause, then a trend bar associated with increased probability of trend start/continuation.
5. **SP2L timing variants:** source material shows both breakout → follow-through → P-Gap and higher-lows/higher-structure → P-Gap variants.
6. **Correction:** after the first directional movement/spike, a correction follows. The official page describes the corrective candle reaching the prior candle's low/high depending on direction.
7. **Entry:** the source supports entry in the direction of the Spike and a pending-limit entry during the correction. The lesson explicitly distinguishes a trigger/event from placing a limit order before activation.
8. **Structural invalidation:** the lesson states that if price returns to the invalidating area, the scenario is cancelled; exact executable level remains unresolved.
9. **Leg structure:** the lesson explicitly discusses Leg 1, Leg 2, nested 2Leg examples, and a larger/deeper parent-leg interpretation.
10. **AB=CD:** the source explicitly identifies 2Leg with AB=CD and presents Leg 2 as approximately matching/projecting from Leg 1.
11. **Reward terminology:** TP1/TP2 and R1/R2 are source terms; 2X/3X are reward-selection examples. They are not frozen as fixed numeric target formulas.
12. **Secondary entry:** the official page states a 50% secondary/add-on entry measured from entry to stop-loss. Its mandatory/optional scope for canonical Strategy A remains unresolved.
13. **Default TP:** the official page states default TP 1:1. This is preserved as source evidence but not reconciled into the lesson's TP1/TP2/R1/R2/AB=CD structure.

## Explicitly unresolved / blocked

- Exact P-Gap endpoint indices and OHLC fields.
- Wick/body/open/close convention for gap measurement.
- Minimum gap size and overlap/tolerance.
- Universal candle-count condition for Pressure Gap.
- Exact machine relation between breakout, FT, and P-Gap.
- Deterministic A/B/C/D anchors and parent-vs-nested scale selection.
- Exact pending-limit price and fill semantics; fill must not be assumed to equal C.
- Exact SL field, boundary, and offset semantics.
- Exact executable TP1/TP2/R1/R2 mapping and its reconciliation with default 1:1.
- Mandatory/conditional/optional status of the 50% secondary entry.

## Prohibited promotions

The following remain explicitly forbidden from production/canonical Strategy A:

- generic three-candle gap formula promoted to P-Gap without source confirmation;
- third-party TradingFinder implementation geometry;
- wick/body inference from pixels;
- generic swing/fractal algorithms for A/B/C/D;
- `fill_price = C` assumption;
- fixed 1R/2R or numeric TP distances derived from examples;
- seven-lower-highs as a universal threshold;
- MA60/M1/M5/session conditions as hard executable gates unless independently source-confirmed.

## Gate decision

**SEMANTIC FREEZE: PASS**  
**FROZEN_GEOMETRY: BLOCKED**

This artifact may guide future source research and synthetic fixtures. It must not be used to generate live BUY/SELL signals or claim historical performance.

## Next gate

**G364 — Source artifact acquisition checklist** remains the required path to resolve the blocked executable dimensions. No production implementation begins before FROZEN_GEOMETRY passes.
