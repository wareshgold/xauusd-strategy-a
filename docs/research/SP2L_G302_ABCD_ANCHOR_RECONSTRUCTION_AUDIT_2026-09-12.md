# SP2L G302 — AB=CD Anchor Reconstruction Audit

**Date:** 2026-09-12  
**Status:** `ABCD_SEMANTIC_CONFIRMED__ANCHORS_AND_TOLERANCE_UNRESOLVED`

## Source finding

The source explicitly supports an AB=CD relationship and second-leg continuation. The source evidence reviewed so far does not uniquely identify executable A, B, C and D price anchors in the continuous worked example.

## Candidate anchor families considered

The following remain candidates only:

- candle open/close anchors;
- wick-extrema anchors;
- body-edge anchors;
- Spike-origin / Spike-end anchors;
- correction reference / Entry anchors;
- combinations of the above.

No candidate is promoted to canonical.

## Current implementation comparison

`LegProjection.ts` currently computes:

`leg1Size = abs(spikeEnd.close - spikeStart.open)`

and projects that magnitude from `correction.extremePrice`. This is a deterministic research hypothesis, but it is not an established source A/B/C/D mapping.

## Tolerance

No source-confirmed AB=CD tolerance has been identified. Therefore exact equality, percentage tolerance, point tolerance, tick tolerance, and rounding policy all remain unresolved.

## Decision

`ABCD_RELATION = SOURCE-CONFIRMED`

`A_ANCHOR = UNRESOLVED`

`B_ANCHOR = UNRESOLVED`

`C_ANCHOR = UNRESOLVED`

`D_ANCHOR = UNRESOLVED`

`ABCD_TOLERANCE = UNRESOLVED`

`ABCD_TO_TP_MAPPING = UNRESOLVED`

No implementation change is authorized.
