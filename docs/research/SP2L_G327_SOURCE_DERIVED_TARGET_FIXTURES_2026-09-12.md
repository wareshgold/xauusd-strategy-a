# SP2L G327 — Source-Derived Target Geometry Fixtures

**Date:** 2026-09-12  
**Status:** `FIXTURES_IMPLEMENTED__NO_CANONICAL_SELECTION`

## Purpose

G327 converts the unresolved 250/500/1000 target-ladder interpretations from G316 into deterministic synthetic fixtures. The purpose is discrimination, not optimization and not historical validation.

The fixtures encode only the currently observed source-shaped facts:

- bullish schematic order: `TP2 > TP1 > Entry > SL`;
- numeric annotations: `250 point`, `500 point`, `1000`;
- the existence of TP1 and TP2;
- no assumption that the annotations are executable XAUUSD price units beyond the synthetic fixture itself.

## Candidate matrix

| Candidate | SL→Entry | Entry→TP1 | Entry→TP2 | SL→TP2 | Status |
|---|---:|---:|---:|---:|---|
| C1 equal ladder | 500 | 250 | 500 | 1000 | deterministic candidate |
| C2 sequential intervals | 250 | 250 | 750 | 1000 | deterministic candidate |
| C3 shifted anchors | 250 | 500 | 1000 | 1250 | deterministic candidate |
| C4 example-only | unresolved | unresolved | unresolved | unresolved | non-mappable |

All candidates use the same synthetic Entry price (3000) so the fixture does not fit different price histories to different interpretations.

## What G327 proves

1. C1, C2 and C3 produce distinct executable geometries.
2. The test machinery can inspect the resulting intervals directly.
3. C4 remains explicitly non-mappable rather than silently falling back to C1.
4. No historical outcome, win rate, expectancy, or drawdown is used to rank the candidates.

## What G327 does NOT prove

The fixtures do **not** prove that C1 is the source meaning. They only demonstrate that the candidate interpretations are deterministic and distinguishable once represented synthetically.

They also do not resolve:

- actual XAUUSD point/tick conversion;
- exact Entry anchor;
- exact SL boundary;
- A/B/C/D anchors;
- AB=CD tolerance;
- Round-Level function or override;
- terminal TP selection;
- pending-limit fill semantics;
- stop/target intrabar semantics;
- SELL-side source mapping.

## Gate decision

`C1 = ALIVE`  
`C2 = ALIVE`  
`C3 = ALIVE`  
`C4 = ALIVE_AS_NON_MAPPABLE`

`CANONICAL_TARGET_FORMULA = UNRESOLVED`  
`FROZEN_GEOMETRY = BLOCKED`  
`DEV = BLOCKED_FOR_CANONICAL_STRATEGY`

## Next step

The next source-resolution task is to search for a source example containing an explicit numeric order plus an unambiguous mapping from plotted levels to Entry/SL/TP1/TP2, or an explicit equation. Historical profitability remains outside the selection process.
