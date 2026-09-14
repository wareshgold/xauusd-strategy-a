# SP2L Source-Resolution Pass 2 — P-Gap and Entry

Date: 2026-09-14

## Scope

This pass advances the next two priority dimensions from the source-resolution priority order:

1. P-Gap executable geometry.
2. Entry anchor geometry.

The pass is documentation/evidence only. No Strategy A engine geometry is implemented.

## P-Gap result

The existing G356 source audit remains the controlling evidence for the current P-Gap dimension.

### Resolved

- `P-Gap` is semantically identified with the source's Pressure Gap concept.
- The generic-gap arithmetic shown in the dedicated gaps lesson remains valid only for that generic-gap example.

### Not resolved

The source still does not uniquely determine:

- exact Pressure-Gap candle index;
- executable OHLC endpoints;
- wick versus body/open/close semantics;
- minimum-size rule;
- overlap/equality/tolerance rule;
- universal candle-count rule;
- deterministic relationship between the Pressure Gap and the SP2L breakout/follow-through sequence.

### Decision

`SOURCE-DOES-NOT-DISCRIMINATE / BLOCKED` at executable P-Gap geometry.

No generic three-candle imbalance formula is promoted to P-Gap.

## Entry result

F8 has now been isolated and adjudicated in `SP2L_F8_ENTRY_ANCHOR_SOURCE_DISCRIMINATION_2026-09-14.md`.

### Resolved

- Correction is the entry phase.
- Canonical execution remains Pending Limit.
- Entry is distinct from Leg-2 start.
- Entry is distinct from structural invalidation.
- The demonstrated bullish source example strongly favors the currently relevant higher-low as the pending-entry reference.

### Not resolved

The source does not uniquely determine a universal executable rule for:

- what makes a low/high "relevant";
- exact candle index;
- exact OHLC price field;
- whether the demonstrated dynamic higher-low behavior generalizes to every bullish variant;
- bearish mirror semantics.

### Decision

`SOURCE-DOES-NOT-DISCRIMINATE` at universal deterministic Entry-anchor level.

The demonstrated dynamic/relevant-higher-low interpretation remains research evidence, not canonical geometry.

## Gate impact

| Gate | Status |
|---|---|
| SOURCE RESOLUTION | **IN PROGRESS — P-Gap and Entry materially narrowed** |
| SYNTHETIC FIXTURES | **F8-F15 defined; F8 additionally adjudicated** |
| FROZEN GEOMETRY | **BLOCKED** |
| DEV | **LOCKED for Strategy A geometry** |
| UNTOUCHED VALIDATION | **LOCKED** |
| ROBUSTNESS/STABILITY | **LOCKED** |
| FRESH HOLDOUT | **LOCKED** |
| PRODUCTION | **LOCKED** |

## Next priority

Proceed to the SL / structural-invalidation executable boundary, then pending-order refresh, trigger classifier, AB=CD/targets, and bearish mirror, without introducing formulas or thresholds not directly supported by source evidence.

## Governance

Source meaning outranks implementation convenience and backtest performance. An unresolved dimension remains unresolved. No historical optimization may select among competing source interpretations. Any future canonical promotion requires explicit manual approval by Ali.
