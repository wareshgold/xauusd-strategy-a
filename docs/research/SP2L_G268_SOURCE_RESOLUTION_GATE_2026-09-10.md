# SP2L G268 — Source Resolution Gate

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `PARTIAL_PASS__FROZEN_EXECUTABLE_GEOMETRY_BLOCKED`

## Batch covered

G265 numeric order-panel reconstruction, G266 target-independence audit, and G267 measurement-label mapping.

## Newly strengthened evidence

1. Practical order panels provide reproducible numerical Entry/S/L/T/P observations.
2. The recurring `0.0 / E / 2x` relationship is numerically coherent: `2x` is the midpoint between the stop-side and Entry references in the observed examples.
3. `1` and `2` remain explicit target-side measurement references in the source visuals.
4. Practical T/P values cannot be universally reconstructed as simple 1R or 2R from the visible Entry/S/L values.

## What is now safe to freeze

### Measurement vocabulary

`0.0`, `E`, `2x`, `1`, and `2` may be recorded as source-correlated measurement labels with the meanings established in G267.

### Pending-limit mechanism

Entry remains a pending-limit reference, not a market-reclaim substitution.

### Structural stop semantic

SL remains structurally placed behind the candle from which the Spike originated.

## What remains blocked

- exact Entry OHLC anchor;
- exact SL OHLC boundary/buffer;
- bearish executable mirror;
- A/B/C/D anchors;
- AB=CD executable equation and tolerance;
- exact Leg 1/Leg 2 anchors;
- terminal TP selector;
- relationship between target labels and executable T/P;
- rounding/spread/partial-close semantics;
- intrabar execution semantics.

## Fail-closed rule

No candidate geometry is promoted because it fits the visible order panel. Any unresolved variable remains `UNKNOWN` until source evidence independently resolves it.

## Gate result

`SOURCE RESOLUTION: PASS_PARTIAL`  
`SYNTHETIC FIXTURES: ALLOWED_FOR_HYPOTHESES`  
`FROZEN GEOMETRY: BLOCKED`  
`DEV: BLOCKED_FOR_CANONICAL_ENGINE`  
`VALIDATION: PROTECTED`  
`PRODUCTION: BLOCKED`

## Next highest-value task

Search the source for a worked example where the teacher explicitly derives a pending Entry price and the corresponding SL/AB=CD/TP construction in the same sequence. If unavailable, preserve the current UNKNOWN boundary rather than infer from screenshots.
