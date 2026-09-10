# SP2L G252 — Round Level / Terminal TP Audit

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `ROUND_LEVEL_CONFIRMED_AS_CONCEPT__TERMINAL_TP_SELECTOR_UNRESOLVED`

## Source pass

Frame-by-frame review of the original SP2L source around 43:20–44:40 shows the teacher annotating `Round level` separately from point-distance examples. The same schematic retains TP2, TP1, Entry and SL as distinct reference levels.

The source therefore supports the existence of a round-level concept and separately discusses point distances. The visual sequence does not provide a deterministic rule stating that terminal TP must be the nearest round level, must be adjusted to a round level, or must equal a fixed point-distance multiple.

## Frozen

- TP1/TP2 reference geometry already established in G250: bullish schematic shows one-risk and two-risk distances from Entry.
- `Round level` is a source-taught target/context consideration.
- Point-distance examples are source-taught as a separate concept.

## Not frozen

- `TP = nearest round level`.
- `TP = round level adjusted TP1/TP2`.
- `250 point = TP1`.
- `500 point = TP2`.
- `1000 point = TP2`.
- Any universal point-distance threshold.
- Any rounding precision or price-grid rule.
- Any priority between TP1, TP2, round level, AB=CD, or another target.
- Terminal TP selection.

## Decision

The correct source-first boundary is to preserve round level and point distance as separate source concepts while leaving terminal TP selection unresolved. No production target selector is authorized from this evidence alone.

### Gates

- SOURCE RESOLUTION: `PASS_PARTIAL`
- B6 reference targets: `PARTIAL_FREEZE`
- B6 terminal TP selector: `BLOCKED`
- FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`
- DEV: `BLOCKED`
- UNTOUCHED VALIDATION: `PROTECTED`
- FRESH HOLDOUT: `PROTECTED`
- PRODUCTION: `BLOCKED`
