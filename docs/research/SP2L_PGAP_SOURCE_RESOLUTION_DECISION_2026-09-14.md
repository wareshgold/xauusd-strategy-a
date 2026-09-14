# SP2L P-Gap Source-Resolution Decision — 2026-09-14

## Decision

**P-Gap executable geometry remains `SOURCE-DOES-NOT-DISCRIMINATE` / BLOCKED.**

The current authoritative evidence resolves the semantic identity `P-GAP ↔ Pressure Gap`, but does not provide a unique executable OHLC/candle-index formula.

## Evidence reviewed

The G356 source audit reviewed the dedicated Poursamadi PriceAction (Gaps) lesson at frame level. The generic bullish-gap teaching explicitly describes the displayed generic example using the high of the candle two bars earlier versus the low of the current candle. However, the Pressure Gap examples do not label their highlighted endpoints with OHLC fields or candle indices. The audit records unresolved wick/body/open/close semantics, minimum size, overlap/tolerance, universal candle-count threshold, and exact machine relation to SP2L breakout/follow-through.

The repository's source-resolution history therefore supports the following distinction:

- Generic gap arithmetic: source-confirmed for the generic-gap example only.
- Pressure Gap semantic category: source-confirmed.
- P-Gap executable formula: not source-confirmed.

## Rejected promotion

Do **not** promote `High[i-2] ↔ Low[i]` (or its bearish mirror) into canonical P-Gap geometry merely because it is executable. Doing so would substitute generic-gap teaching for the distinct Pressure Gap category.

Do not infer wick/body, open/close, minimum-size, overlap, tolerance, or candle-count rules from chart pixels or contextual wording.

## Gate impact

- P-Gap semantic identity: **RESOLVED**
- Generic-gap formula: **RESOLVED only for generic gap**
- P-Gap executable endpoint geometry: **BLOCKED**
- FROZEN_GEOMETRY: **BLOCKED**
- Strategy A implementation/backtest selection: **LOCKED**

## Reopen condition

P-Gap geometry may be reconsidered only if a new authoritative source artifact explicitly ties Pressure Gap to executable candle-index/OHLC endpoint semantics or another deterministic charting rule.

## Governance

This decision does not canonicalize a Strategy A P-Gap formula. Manual approval by Ali remains required for any future canonical promotion. No profitability, optimization, or historical backtest result was used in this decision.
