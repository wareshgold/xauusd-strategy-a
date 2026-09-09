# SP2L Semantic Freeze — G27 — 2026-09-09

## Purpose
Freeze only the source-confirmed semantic architecture of Strategy A. This document is not an executable production specification and must not be used to justify invented OHLC formulas.

## Frozen semantic model

1. **Context / market range** is part of setup interpretation; trading inside an unsuitable range is not promoted as canonical execution behavior.
2. **Directional sequence** is represented structurally: bullish examples use Higher Lows; bearish examples use the directional mirror with Lower Highs.
3. **Breakout + follow-through** is a source-recognized event sequence.
4. **P-Gap** is a first-class source concept associated with valid breakout. It is not frozen as generic three-candle FVG/imbalance.
5. **Correction** follows the first directional leg/spike structure.
6. **Entry mechanism** is a pending Limit order during the correction. Market-close reclaim is not an equivalent implementation.
7. **Entry location** is a relevant structural Low/High in the demonstrated sequence, but the universal OHLC anchor is unresolved.
8. **Stop / invalidation** is structural and distinct from Entry. Risk percentage determines sizing, not structural invalidation.
9. **Pending order management** may delete/replace an order when the relevant structural/risk distance changes materially; deterministic threshold and timing remain unresolved.
10. **Trigger family** includes one-, two-, and three-candle examples plus key-bar language; exact acceptance/timing is unresolved.
11. **Leg 1 → Leg 2** is the source's two-leg continuation model.
12. **AB=CD** explicitly links Leg 2 magnitude to Leg 1 magnitude. A/B/C/D anchors and tolerance remain unresolved.
13. **TP1** is preferred in the demonstrated source practice; TP2 is a larger objective and remains a research/backtest candidate. Exact projection formula is unresolved.
14. **2X** is source-confirmed as a concept involving progression toward the target / half-target context, but its exact executable formula is unresolved.

## Production prohibition

No BUY/SELL detector may be promoted from this semantic freeze until the remaining geometry blockers are independently resolved from source evidence or explicitly accepted as a versioned unresolved state that prevents execution.

## Required provenance

Every future executable rule must link to: source timestamp/frame evidence → semantic clause above → deterministic geometry decision → fixture test → validation gate.

## Gate

SOURCE RESOLUTION: semantic freeze achieved.

FROZEN GEOMETRY: blocked.

DEV and all later gates remain locked.
