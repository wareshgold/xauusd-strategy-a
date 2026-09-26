# F10 — Stop Anchor Source Ceiling Decision

Date: 2026-09-26
Status: SOURCE CEILING / UNRESOLVED

## Decision

The final targeted source pass does not provide primary evidence that uniquely selects an executable stop anchor among:

- correction extreme;
- original/base structural low/high;
- wick extreme;
- body/open/close boundary;
- structural swing composed of multiple candles;
- fixed/non-fixed buffer.

The primary transcript confirms a separate stop distance and describes return to the invalidation area as cancelling the scenario. It also describes a pending Buy Limit whose stop distance is known before activation and may be recalculated when subsequent structure changes. However, the available source text does not expose the exact OHLC point used for that invalidation.

The archived visual-resolution decision likewise records exact stop OHLC semantics and buffer as unresolved.

## Important implementation finding

Current research code uses correction extreme as the stop reference. This is explicitly **not** accepted as canonical. No replacement formula is introduced in this checkpoint.

## Evidence boundary

The source pass can establish:

1. Entry and SL are separate concepts.
2. SL is structural invalidation, not a fixed pip/risk-derived distance.
3. Pending-order stop distance is part of the setup before activation.
4. Subsequent structural development can change the order/stop relationship.

It cannot establish:

1. exact candle/index;
2. wick/body/OHLC semantics;
3. structural-turn vs candle anchor;
4. buffer/spread treatment;
5. exact bearish mirror.

## Gate action

F10 is now closed at source ceiling rather than being resolved by inference.

- F10: SOURCE CEILING / UNRESOLVED
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

The F10 discrimination fixtures remain as research safeguards and must not be used to select a canonical rule without new primary evidence.

## Reopen condition

Reopen F10 only if new primary author evidence explicitly shows or states the stop marker/anchor, its OHLC semantics, or its buffer semantics.
