# G374 — Source Closure Decision

Date: 2026-09-13
Status: SOURCE RESOLUTION / gate decision
Canonical: false

## Decision
**FROZEN GEOMETRY: BLOCKED.**

The currently available authoritative corpus establishes the semantic SP2L framework but does not provide enough explicit geometry to freeze a reproducible Strategy A implementation without invention.

## Remaining blockers
1. P-Gap executable endpoints, overlap and size/tolerance.
2. A/B/C/D anchor definitions and canonical parent/nested scale.
3. Exact pending-limit price and fill semantics.
4. Exact structural SL boundary and any offset.
5. TP1/TP2/R1/R2 mapping versus official 1:1 default and AB=CD projection.
6. Scope of the official 50% secondary entry for the primary signal.

## Prohibited promotions
- Generic gap formula as P-Gap.
- Guessed A/B/C/D anchors.
- `fill_price = C` by convention.
- Guessed SL offset.
- Fixed 2X/3X target constants.
- Generalized seven-lower-high rule.
- Unconfirmed MA/session/timeframe hard gates.

## Gate consequences
- Canonical DEV/VAL backtesting: **not authorized**.
- Production/live signal generation: **not authorized**.
- Non-canonical hypothesis research: **authorized**, provided every hypothesis remains explicitly non-canonical and cannot be promoted by performance.

## Recommended next action
Attempt one final primary-artifact acquisition only if a higher-resolution/annotated source can realistically expose the missing geometry. Otherwise maintain the semantic freeze and proceed with controlled non-canonical hypothesis research rather than manufacturing a frozen strategy specification.
