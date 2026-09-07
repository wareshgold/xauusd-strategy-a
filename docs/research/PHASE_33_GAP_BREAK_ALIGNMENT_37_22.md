# Phase 33 — SP2L Gap / Level-Break Alignment (37:22)

**Date:** 2026-09-07  
**Branch:** `research/phase12-preentry-geometry-robustness`  
**Status:** Research/source synchronization only — no production implementation

## 1. Source evidence

The Poorsamadi SP2L source example around **37:22** shows, in the supplied chart image, a directional break from a relevant level occurring together with a visible gap.

Source-grounded semantic statement:

`relevant level break + gap occurrence can be simultaneous in the demonstrated setup`

This is visual evidence about sequence/alignment. It is **not** by itself a numeric definition of the gap.

## 2. What this strengthens

The example supports keeping the following concepts connected in the research model:

- a level/context exists before the directional break;
- the directional move can break that level while a gap is present at the same transition;
- gap evidence may therefore belong to the breakout/pressure-movement context rather than being treated as an isolated candle pattern.

This is consistent with the existing source-grounded distinction between P-GAP pressure evidence and exhaustion gaps.

## 3. What this does NOT establish

The 37:22 image does **not** provide a defensible machine-readable value for:

- minimum gap size;
- body-to-body versus wick-to-wick measurement;
- required non-overlap percentage;
- exact candle-index formula;
- exact level-selection lookback;
- exact session window;
- exact P-GAP classification threshold;
- mandatory/optional status of the gap for every SP2L branch.

No such rule is added to production from this image.

## 4. Research consequence

For SP2L V2, represent this as source evidence attached to the breakout/pressure-gap branch:

`CONTEXT / LEVEL -> BREAKOUT / STRONG MOVE -> simultaneous gap evidence -> SPIKE FAMILY`

The gap remains a contextual discriminator until its exact source geometry is recovered. Historical performance must not be used to invent the missing geometry.

## 5. Geometry gate

This evidence does **not** resolve the outstanding SP2L geometry gates:

- G4 — exact Leg1 endpoints: TBD;
- G5 — exact Leg2 projection origin: TBD;
- G6 — numerical equality tolerance: TBD;
- exact P-GAP geometry: TBD.

## 6. Protected boundaries

- No Strategy A production code changed.
- No historical DEV/VAL optimization performed.
- Fresh Holdout remains locked.
- No numerical gap threshold was inferred from the chart.

**Decision:** source synchronization improved; deterministic gap geometry remains unresolved.
