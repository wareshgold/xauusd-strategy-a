# SP2L Batch 45 — P-Gap Evidence Closure Decision — 2026-09-21

## Objective

Perform the final targeted closure attempt for the current P-Gap executable
geometry blocker by cross-checking the archived primary-source records against
the author-owned implementation.

This is a source-resolution decision record only. No performance data is used
to choose a rule, and no canonical strategy code is changed.

## Evidence set

### Primary source

Archived records report:

- P-Gap is explicitly named and distinguished from E-Gap.
- `Valid BO = P-Gap` is explicitly visible in the teaching sequence.
- P-Gap is taught in a pressure/trend context involving pressure, a pause or
  compression, and a subsequent trend-bar/continuation structure.
- Multiple ordering variants are shown.
- The primary material does **not** expose a machine-readable OHLC formula,
  exact candle indices, numeric gap threshold, wick/body endpoint semantics,
  or a complete bearish mirror.

### Author-owned implementation

The inspected author implementation explicitly encodes:

- `-4` = candle before spike
- `-3` = spike candle
- `-2` = candle after spike
- `-1` = latest candle

P-Gap candidate:

- BUY: `low[-2] > high[-4] + P_GAP_PRICE`
- SELL: `high[-2] < low[-4] - P_GAP_PRICE`

The implementation also contains directional spike/body conditions and a
second-leg local-break condition.

The implementation's threshold is configurable
(`pGapSize` / `PGAP_POINTS` / `P_GAP_PRICE` depending on revision), so
the presence of the formula does not establish a canonical numerical
threshold.

## Closure matrix

| Question | Primary source | Author implementation | Closure |
|---|---|---|---|
| P-Gap is a valid-breakout/pressure-gap concept | Explicit | Explicitly implemented | **CLOSED — concept only** |
| Four-candle indexing | Not explicitly machine-labelled | Explicit `-4/-3/-2/-1` | **NOT CLOSED as canonical source rule** |
| BUY OHLC endpoints | Not explicitly stated | `low[-2]` vs `high[-4]` | **NOT CLOSED as canonical source rule** |
| SELL OHLC endpoints | No source-complete mirror | `high[-2]` vs `low[-4]` | **NOT CLOSED as canonical source rule** |
| Wick/body semantics | Not specified | Uses OHLC high/low | **NOT CLOSED** |
| Gap threshold | Not specified | Configurable parameter | **NOT CLOSED** |
| Compression boundary | Qualitatively shown/described | Implementation-specific body/sequence tests | **NOT CLOSED** |
| Trend-bar executable definition | Concept confirmed | Body-size comparisons/configuration | **NOT CLOSED** |
| P-Gap formula binding | Label and concept confirmed | Formula explicitly implemented | **NOT CLOSED — missing primary binding** |

## Deterministic finding

The investigation has reached the evidence limit of the currently archived
primary material.

There is strong convergence between the primary teaching concept and the
author implementation, but convergence is **not** equivalent to a primary
source statement binding the exact formula to P-Gap.

Therefore the canonical status remains:

**P-Gap concept: SOURCE-CONFIRMED**

**P-Gap executable formula: AUTHOR-IMPLEMENTATION-SUPPORTED / PRIMARY-SOURCE-UNRESOLVED**

**Canonical P-Gap detector: NOT FROZEN**

## Important negative finding

The generic gap convention recorded in the source material must not be used as
a substitute for the author implementation's P-Gap construction. The generic
gap example and the author-code P-Gap formula are separate evidence items.

Likewise, the author implementation's configurable values must not be promoted
to source rules merely because they are explicit in code.

## Gate decision

**Source Resolution: PARTIAL**

**Frozen Geometry: BLOCKED**

**Untouched Validation: LOCKED**

**Robustness/Stability: LOCKED**

**Fresh Holdout: LOCKED**

**Production: OFF**

No BUY/SELL production logic is changed.

## Next permitted path

The project should stop trying to resolve this specific P-Gap formula through
backtest comparison or parameter tuning.

If no new primary-source evidence becomes available, the implementation may
retain the author formula only as a clearly labelled **research candidate**.
Canonical freeze must wait for direct source binding or an explicitly approved
source-resolution change.

The next independent geometry blocker remains F14 AB=CD anchor resolution;
however, P-Gap remains a prerequisite dependency for the full Strategy A
freeze.
