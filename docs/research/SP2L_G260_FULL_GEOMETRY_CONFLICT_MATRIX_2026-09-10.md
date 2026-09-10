# SP2L G260 — Full Geometry Conflict Matrix

**Date:** 2026-09-10
**Gate:** SOURCE RESOLUTION
**Status:** `PARTIAL_FREEZE__EXECUTABLE_GEOMETRY_BLOCKED`

## Purpose

Consolidate the current source evidence for Entry, Structural SL, AB=CD, Leg 2 and target references without allowing one unresolved component to silently define another.

## Current matrix

| Component | Source status | Executable status | Prohibited inference |
|---|---|---|---|
| Spike | source-defined directional movement | unresolved full detector | invented magnitude threshold |
| P-Gap | first-class validity condition | geometry partially frozen; full predicate unresolved | generic FVG/imbalance equivalence |
| Correction | bullish reaches prior low; bearish prior high | reference event known, exact execution anchor unresolved | Entry = correction extreme |
| Buy Limit | explicit pending order mechanism | exact price anchor unresolved | market-entry substitution |
| Entry | explicit order field/reference | unresolved | C/fill/E/2x without source proof |
| Structural SL | behind Spike-origin candle | exact OHLC boundary unresolved | wick/body/buffer by symmetry |
| AB=CD | explicit source relationship | A/B/C/D unresolved | D=TP or C=Entry |
| Leg 2 | second directional continuation | projection equation unresolved | invented projection |
| TP1 | explicit source target concept | reference geometry requires source audit | assume terminal TP=TP1 |
| TP2 | explicit source target concept | reference geometry requires source audit | assume terminal TP=TP2 |
| Round level | source-defined concept | selector unresolved | nearest-round-level rule |
| Point distance | source-defined concept | selector unresolved | 250/500/1000 = TP levels |
| Terminal TP | explicit practical order field | selection rule unresolved | TP=2R / AB=CD / round level |

## Cross-component conflicts that must remain open

1. **Entry ↔ AB=CD:** no evidence establishes C = Entry.
2. **SL ↔ 2R:** risk can be computed only after exact Entry/SL execution anchors are frozen.
3. **AB=CD ↔ terminal TP:** AB=CD is source-confirmed, but target identity is not.
4. **TP1/TP2 ↔ terminal TP:** visible target references do not prove which one becomes the terminal order TP.
5. **Round level ↔ terminal TP:** round-level teaching does not yet establish a deterministic TP selector.
6. **Measurement labels ↔ execution:** `0.0 / 2x / E / 1 / 2` remain source-correlated vocabulary; they cannot be promoted solely from numerical coincidence.

## Consistency rule

A candidate full geometry is admissible only if every component is independently source-supported. A profitable or internally elegant combination is not evidence of source meaning.

## Gate decision

SOURCE RESOLUTION: `PASS_PARTIAL`

FROZEN GEOMETRY: `BLOCKED_FOR_FULL_STRATEGY`

DEV: `BLOCKED`

UNTOUCHED VALIDATION: `PROTECTED`

ROBUSTNESS / STABILITY: `BLOCKED`

FRESH HOLDOUT: `PROTECTED`

PRODUCTION: `BLOCKED`

## Next research boundary

The highest-value unresolved question is not another backtest. It is a source-quality cross-reference that can simultaneously expose the teacher's Entry construction, origin-candle SL placement, AB=CD measurement anchors, and terminal TP selection in one continuous worked example. Until that is available, keep the engine fail-closed.