# Phase 33 — SP2L G2 Pending-Limit Resolution

**Date:** 2026-09-06  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Candidate geometry resolution — research only

## Objective

Resolve the next SP2L geometry question:

> What price level becomes the pending-limit entry after the spike creates a valid higher-low / lower-high structure?

## Source evidence

Public SP2L descriptions state that, during a bullish spike, consecutive higher lows create potential buy-entry levels, while during a bearish spike, consecutive lower highs create potential sell-entry levels. They further state that the entry is activated when price returns to retest that level. citeturn0search0turn0search2

The source therefore supports this semantic relationship:

```text
BULLISH: HL low -> candidate Buy Limit
BEARISH: LH high -> candidate Sell Limit
price returns to level -> entry activation
```

This is materially stronger than the earlier interpretation that a single generic "first structural low/high" must be the universal entry level.

## G2 candidate

The research candidate is:

```text
Bullish candidate entry = low of a supplied higher-low candle.
Bearish candidate entry = high of a supplied lower-high candle.
```

Implementation:

`src/domain/research/sp2l-v2/PendingLimitCandidate.ts`

The helper intentionally does **not** decide:

- how the spike is detected;
- how the HL/LH sequence is detected;
- which of multiple valid HL/LH levels should be selected;
- how long a pending order remains valid;
- whether a touch uses wick, bid/ask, or another execution convention;
- whether tolerance is allowed.

Those remain separate unresolved questions.

## Exact retest fixture

The current research fixture deliberately uses exact equality only:

```text
price == pendingEntryPrice -> retest
price != pendingEntryPrice -> no retest
```

This is a simulator fixture, **not** a production execution rule. No tolerance is introduced without source evidence.

## Important correction to G1 interpretation

The Phase 33 G1 candidate remains valid as a **candle-reference primitive**, but it must not be interpreted as a universal single reference. The public description allows multiple potential levels because each successive HL/LH can become a candidate entry level. citeturn0search0turn0search2

Therefore:

```text
G1 = identify/reference a valid HL/LH candle level
G2 = convert that level into a pending-limit candidate
```

The generic multi-candle pivot algorithm remains TBD.

## Decision

**G2 candidate accepted for further source review.**

No historical XAUUSD data was used to select this interpretation.

## Protected boundaries

- Fresh Holdout remains LOCKED.
- Phase 13–32 reports remain immutable historical/architectural evidence.
- Production Strategy A remains untouched.
- No EMA50/EMA100 rule is promoted.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result decides source meaning.

## Next step

G3 — resolve the structural stop reference. The source indicates that the stop is placed behind the candle where the spike originated, but the exact price/buffer and intrabar touch semantics remain unresolved.
