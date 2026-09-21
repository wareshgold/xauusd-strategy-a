# SP2L F10 — Invalidation / Stop-Loss Anchor Resolution Audit — 2026-09-19

## Purpose

Resolve F10 using only source-aligned evidence already archived in the repository. The objective is to determine whether the source uniquely specifies the executable stop-loss price and invalidation condition.

No wick/body convention, buffer, spread adjustment, pip offset, or price formula is inferred from backtest performance or implementation convenience.

## Evidence reviewed

- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_SOURCE_RESOLUTION_GAP_REGISTER_F11_F14_PGAP_2026-09-16.md`

## Source-confirmed findings

### 1. SL is tied to the candle from which the spike originated

The author-associated source states that after the Second Leg is triggered, entry is taken in the spike direction and the SL is placed **behind the candle from which the spike originated**.

This is materially stronger than a generic risk-management assumption.

**Status:** SL structural anchor = **SOURCE-CONFIRMED at concept level**.

### 2. The primary teaching diagram separately shows Buy Limit and SL

Batch34 records a horizontal level labelled `Buy Limit` and a separate lower horizontal reference labelled `SL`.

This confirms that the source distinguishes the entry/order level from the stop-loss reference.

**Status:** Entry-vs-SL separation = **SOURCE-CONFIRMED**.

### 3. The source describes invalidation through return toward the referenced level

The transcript explains that the stop distance is known before activation because a return to the referenced level invalidates the scenario.

This supports the existence of an invalidation relationship between price returning through the relevant origin/SL structure and the SP2L setup.

However, the archived wording does not uniquely specify whether invalidation is defined by:

- intrabar wick penetration;
- candle close beyond the level;
- bid/ask crossing;
- exact equality/touch;
- a buffered breach.

**Status:** invalidation concept = **SOURCE-SUPPORTED**, executable event = **UNRESOLVED**.

## Exact price-boundary test

The source evidence reviewed does **not** uniquely state whether “behind the candle” means:

- candle Low for bullish setups / candle High for bearish setups;
- wick extreme plus a buffer;
- body boundary;
- open/close;
- another structural level associated with the origin candle;
- broker-side spread-adjusted level.

No source-confirmed numeric buffer, pip distance, point distance, ATR offset, or spread rule was found in the archived evidence.

Therefore the exact executable SL price cannot be frozen.

## Directional mirror

The author-associated source gives the directional concept that the SL sits behind the spike-origin candle. The bullish example is explicit in the archived forensic material, while a complete source-complete bearish price-field mirror is not explicitly demonstrated in the same primary sequence.

Thus the semantic mirror is supported, but the exact OHLC field for both directions remains unresolved.

## Invalidation vs execution stop

The source supports the conceptual relationship:

`spike-origin structure → SL / invalidation boundary`

It does **not** establish whether the trading stop must be placed exactly at that boundary, slightly beyond it, or according to a platform-specific buffer.

Likewise, the source does not establish broker-level execution semantics such as bid/ask, spread, slippage, partial fill, or stop-trigger timing.

These remain outside canonical Strategy A until source evidence resolves them.

## Deterministic F10 test

| Required element | Source status |
|---|---|
| SL is related to spike-origin candle | SOURCE-CONFIRMED |
| Entry and SL are separate levels | SOURCE-CONFIRMED |
| Return through relevant structure invalidates setup | SOURCE-SUPPORTED |
| Exact bullish SL price field | UNRESOLVED |
| Exact bearish SL price field | UNRESOLVED |
| Wick vs body semantics | UNRESOLVED |
| Buffer / offset | UNRESOLVED |
| Touch vs penetration vs close | UNRESOLVED |
| Bid/ask execution semantics | UNRESOLVED |
| Spread/slippage handling | UNRESOLVED |

## Deliberate non-inferences

This audit does **not** promote:

- `SL = spike candle Low` as canonical;
- `SL = spike candle High` as canonical;
- any fixed pip/point buffer;
- any 50–80 pip source rule as a canonical geometry rule;
- candle-close invalidation;
- wick-touch invalidation;
- broker-specific stop semantics;
- backtest-derived SL offsets.

## F10 result

**PARTIAL / UNRESOLVED**

The source now supports a clear structural statement:

> SL is associated with / placed behind the candle from which the spike originated.

But the evidence does not uniquely determine the exact price field, buffer, or executable invalidation event.

Therefore F10 cannot be promoted to SOURCE_CONFIRMED executable geometry.

## Gate impact

- F10: **PARTIAL / UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- No new backtest/optimization is justified.
- No canonical SL formula is promoted.
- `LIVE_TRADING_ENABLE=false` remains unchanged.

## Next source-resolution priority

The next unresolved executable blocker is **F12 — Trigger acceptance / precedence**, while the exact P-Gap formula remains the highest-severity unresolved geometry item overall.

F12 should be tested for whether the source uniquely determines when the Second Leg is considered triggered and how one-, two-, and three-candle variants are prioritized.

## Decision

**F10 remains PARTIAL / UNRESOLVED.**

The research implementation must not be promoted to canonical Strategy A geometry from this evidence.
