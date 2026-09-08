# SP2L Source Entry Cross-Check — 2026-09-08

## Purpose

This document records a primary-source audit of the SP2L entry semantics, with one specific discrimination question:

> Is the pending-limit entry contingent on a later breakout/reclaim of the last Spike candle, or is the order made available during the correction itself?

This is source-resolution work only. Backtest profitability is not used to define source meaning.

## Primary source

- Uploaded source video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: approximately 69:15.7
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

The primary video remains authoritative over secondary TradingFinder implementations.

## Primary-source evidence

### 38:38 — correction creates order opportunity

The instructor describes the next candle beginning correction as price moving below the first Low in the bullish example, and says an order can be placed there manually or as a pre-set limit. The bearish case is presented as the mirror toward the relevant High.

### 39:11–39:26 — no later candle/reclaim is required before order placement

The instructor explicitly says there is no need to wait for the next candle and that the order can be placed within the initial three-candle sequence. The Buy Limit is then shown as already placed, with the stop distance known before activation.

This is direct evidence for a pending-order state that exists while the correction develops.

### 39:48–40:07 — order can be revised while setup develops

The instructor discusses deleting/replacing the order if the next candle changes the stop distance, including changing order size when the distance becomes too large. This behavior is consistent with a resting pending order rather than a mandatory later breakout/reclaim trigger.

### 46:15–47:56 — correction-based entry repeated

The later teaching section again describes correction toward the previous/relevant Low for BUY and previous/relevant High for SELL and identifies that level as the important entry level for the second leg.

## Visual cross-check

The source diagrams around the Buy Limit section visibly annotate `Buy Limit` on a horizontal order level during the developing bullish sequence, with `SL` below the early/origin structure. The diagram does not establish a mandatory later last-Spike-candle reclaim before order placement.

The later Entry/SL/TP diagram similarly shows an Entry level reached during correction. It does not uniquely reveal the exact OHLC formula for that horizontal level.

## Four initial real-trade examples

The later real-XAUUSD section contains an order-history table with four initial trades. The visible records include approximately:

- Entry 3229.08, SL 3237.73, TP 3213.37
- Entry 3223.84, SL 3235.50, TP 3213.37
- Entry 3228.88, SL 3235.50, TP 3213.37
- Entry 3232.41, SL 3237.80, TP 0

These examples corroborate that actual orders and subsequent management were demonstrated.

However, the recorded chart view and annotations do not provide a sufficiently precise, candle-indexed audit trail for each of the four trades to prove whether a last-Spike-candle reclaim occurred before or after order placement/fill. Therefore these examples are supporting evidence only and are **not** used to freeze executable geometry.

They also show multiple management states; they must not be used to infer one universal entry/exit formula.

## Discrimination result

### H-LSCB — Last-Spike-Candle Breakout hypothesis

`SPIKE → CORRECTION → BREAK/RECLAIM OF LAST SPIKE CANDLE → ENTRY`

**Status: REJECTED AS CANONICAL SOURCE ENTRY SEMANTIC.**

Reason: the primary source explicitly describes placing a Buy Limit during correction and explicitly says there is no need to wait for another candle. A mandatory later reclaim is therefore not supported as a prerequisite by the highest-authority evidence currently available.

### Source-aligned baseline

`SPIKE → CORRECTION → PENDING LIMIT AVAILABLE/PLACED → FILL IF PRICE REACHES ORDER`

**Status: SOURCE-CONFIRMED SEMANTIC.**

The exact price formula remains unresolved.

## What remains unresolved

Do not freeze any of the following without stronger source evidence:

- exact candle index represented by `previous/relevant Low/High`;
- exact Entry price: wick, body, level, or another source-defined point;
- whether the entry reference is always the first correction reference or can move to a later candle;
- exact pending-order cancellation/expiry semantics;
- exact fill semantics when a candle trades through the pending level;
- exact SL wick/body convention and buffer;
- exact P-Gap OHLC boundary and timing;
- exact Leg-1 anchors;
- exact AB=CD tolerance.

## Gate decision

| Item | Status |
|---|---|
| Pending-limit entry semantic | **SOURCE_CONFIRMED** |
| Entry requires later last-Spike-candle reclaim | **REJECTED_AS_CANONICAL** |
| Exact Entry price | **UNRESOLVED** |
| Exact Entry candle index | **UNRESOLVED** |
| Frozen executable geometry | **BLOCKED** |
| Historical optimization | **LOCKED** |
| DEV / VAL / Holdout promotion | **LOCKED** |
| Production changes | **NONE** |

## Next highest-value source-resolution step

Resolve the **exact Entry level geometry** from the primary source. Candidate interpretations should be limited to source-observable candle/OHLC relationships and tested on synthetic fixtures before any historical optimization.

No generic FVG, Fibonacci C point, 50% retracement, market-close reclaim, or last-Spike-candle breakout rule may be substituted for unresolved source geometry.

## Source hierarchy rule

If a secondary implementation conflicts with the primary source video, the primary source controls. A profitable secondary interpretation must not be promoted merely because it backtests better.
