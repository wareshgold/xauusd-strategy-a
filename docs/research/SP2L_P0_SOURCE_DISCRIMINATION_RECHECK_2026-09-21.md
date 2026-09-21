# SP2L P0 Source Discrimination Recheck — F08/F10 — 2026-09-21

## Purpose
Recheck whether the currently archived source boundary permits deterministic promotion of F08 Swing or F10 Stop.

## F08
Source-supported meaning:
- directional legs are associated with visible structural turning/reference areas;
- evolving higher-low/lower-high structure is relevant;
- the source does not uniquely specify a universal pivot algorithm, lookback, index, tie-break, or wick-vs-body endpoint.

Competing deterministic interpretations therefore remain unresolved:
- structural turning area vs fixed pivot window;
- wick extreme vs body endpoint;
- candidate precedence where multiple turns exist;
- asymmetric bullish/bearish windows.

**Decision: F08 remains UNRESOLVED.**

## F10
Source-supported meaning:
- stop is placed behind the candle from which the spike originated.

The archived evidence does not uniquely establish:
- wick vs body field;
- numeric buffer/spread adjustment;
- touch vs breach vs close invalidation;
- exact spike-origin mapping when the spike spans multiple candles.

A prior research record explicitly prohibits choosing these by profitability or parameter optimization.

**Decision: F10 remains UNRESOLVED.**

## Canonicalization guard
No implementation, backtest, or synthetic fixture is sufficient to promote either F08 or F10 without new discriminating primary-source evidence.

## Gate
- F08: UNRESOLVED
- F10: UNRESOLVED
- Frozen Geometry: BLOCKED
- Canonical Strategy A: NOT READY
- Production: DISABLED

## Next permissible action
Seek additional primary-source evidence specifically capable of distinguishing the competing hypotheses. Do not tune or select among them from backtest performance.
