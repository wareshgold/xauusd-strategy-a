# SP2L Transcript Cross-Resolution — 2026-09-14

## Status

RESEARCH-ONLY. No canonical geometry promotion. No engine changes. No optimization. No production BUY/SELL decisions.

## Tier-1 transcript

Authoritative uploaded artifact: `پورصمدیSP2L TRANSCIBE.txt`.

The transcript explicitly requires candle-by-candle reading; this constrains us against replacing source geometry with a coarse wave abstraction.

## Resolved semantics

### Breakout / P-GAP
The source defines breakout using close + follow-through behavior and identifies P-GAP as a simple sign of breakout, explicitly distinguishing P-GAP from E-GAP/Common-GAP. Exact P-GAP OHLC formula, candle indices, and invariants remain unresolved.

### Entry / correction / Leg 2
At 38:38 the source describes correction as moving below the first low in the bullish example. At 38:53–39:11 it describes gap + breakout + follow-through and says a limit order can be placed within the first three candles. Exact executable entry price anchor and universal mapping to Leg-2 start remain unresolved.

### Invalidation / SL
At 39:26 the source ties scenario invalidation to a return to the cited structural level and separately represents SL. Exact OHLC/wick/body boundary remains unresolved.

### Pending-order refresh
At 39:48–40:16 the source describes deleting/replacing a pending order after a later candle, while also retaining/moving it when the distance is not sufficiently harmful to money management. Behavior is source-confirmed; deterministic threshold/algorithm is unresolved.

### Trigger family
The source discusses one-, two-, and three-candle constructions and allows the limit order within the first three candles in the described sequence. Exact acceptance classifier remains unresolved.

### AB=CD / Leg 2
At 37:57 the source expects the next leg to be built to the same size as the preceding leg. Therefore the semantic relation `Leg2Magnitude ≈ Leg1Magnitude` is supported. A/B/C/D anchors and equality tolerance remain unresolved.

### 2X / TP1 / TP2
The transcript explicitly demonstrates/discusses 2X and TP1/TP2 concepts. Exact executable target formulas remain unresolved.

### Bearish mirror
Bearish lower-high / sell examples are present, but a fully deterministic sign-inverted mirror for every bullish rule is not uniquely established.

## Video cross-check

Previously registered direct source-video evidence covers 36:59–37:22 (Valid BO = P-Gap / AB=CD association), 38:40–39:50 (Buy Limit and SL representation), 1:02:41–1:03:32 (bearish structure), and 1:04:00–1:04:32 (bearish order/continuation). The transcript strengthens semantic interpretation but does not make the remaining executable geometry unique.

## Canonicalization gate

| Dimension | Source status | Executable status |
|---|---|---|
| Breakout / follow-through | Confirmed | Exact indexing unresolved |
| P-GAP | Confirmed concept | Formula/indexing unresolved |
| Entry correction | Confirmed concept | Exact anchor unresolved |
| Leg-2 start | Semantically separated | Exact endpoint unresolved |
| Structural invalidation | Confirmed concept | Exact OHLC boundary unresolved |
| Pending refresh | Confirmed behavior | Threshold/algorithm unresolved |
| 1/2/3-candle trigger family | Confirmed | Classifier unresolved |
| AB=CD | Magnitude relation supported | Anchors/tolerance unresolved |
| 2X / TP1 / TP2 | Concepts confirmed | Formula unresolved |
| Bearish mirror | Examples confirmed | Deterministic mirror unresolved |

## Conclusion

The newly confirmed transcript materially strengthens source evidence but does not satisfy the canonicalization gate. No competing geometry hypothesis may be selected by backtest performance. Remaining ambiguity stays explicitly unresolved pending discriminating Tier-1/2 evidence and manual canonical approval.
