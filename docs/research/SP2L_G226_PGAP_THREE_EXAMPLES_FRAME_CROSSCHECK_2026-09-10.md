# SP2L G226 — P-Gap Three-Example Frame Cross-Check

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION  
**Status:** `P-GAP_GEOMETRY_STILL_UNRESOLVED`

## Objective

Inspect the three numbered P-Gap examples in the raw SP2L teaching sequence (~35:55–36:16) against the same-author generic Gap definition recovered from the comprehensive Gap course.

The purpose is to narrow the geometry hypothesis space without converting visual similarity into a canonical production formula.

## Source evidence

The comprehensive Gap course explicitly describes a bullish generic Gap by comparing the **high of the candle two bars before** with the **low of the current candle**. A gap exists when there is a price distance between those two levels. Research candidate:

`High[t-2] < Low[t]`

The raw SP2L sequence explicitly states:

`Valid BO = P-Gap`

and displays three numbered examples plus an invalid example marked with a red X.

## Example-by-example visual cross-check

### Example 1

The shaded P-Gap zone is drawn across the local bullish candle sequence. Its apparent boundaries are consistent with a separation between an earlier candle's upper extreme and a later/current candle's lower extreme. The construction is visually compatible with a three-candle high[t-2] / low[t] separation.

The schematic is not numerical OHLC data and the rectangle is a teaching overlay. Exact wick endpoints and candle indices therefore cannot be recovered uniquely.

**Result:** `COMPATIBLE`, not `PROVEN`.

### Example 2

The second numbered construction again shows a bullish sequence with a shaded horizontal gap zone. The hand-drawn marks point toward extrema in the local sequence and the zone is compatible with the same generic three-candle relation.

The exact participating indices and whether the zone edges represent wick extrema, body edges, or a simplified teaching rectangle remain unresolved.

**Result:** `COMPATIBLE`, not `PROVEN`.

### Example 3

The third numbered construction is the clearest visual match. The shaded zone lies between an earlier candle's upper level and a later/current candle's lower level, while the handwritten marks point to the relevant extrema. This is consistent with the generic Gap-course relation `High[t-2] < Low[t]` for a bullish case.

No numerical OHLC values are present in the schematic, so exact equality of rectangle boundaries to those extrema cannot be established from pixels alone.

**Result:** `STRONGLY_COMPATIBLE`, not `PROVEN`.

## Invalid example / red-X comparison

The leftmost invalid construction does not show the same clean separation between the relevant candle extrema. The red X is direct negative teaching evidence, but the failed predicate is not uniquely recoverable from the schematic.

Possible explanations include insufficient separation, different candle indexing, or an additional contextual requirement. None is promoted to canonical.

## Cross-example conclusion

All three numbered P-Gap diagrams are visually compatible with the same-author generic Gap relation `High[t-2] < Low[t]` for bullish cases. This is stronger than a one-example coincidence, but still not source-unique proof.

The evidence does **not** yet prove:

- `P-Gap = Generic Gap`;
- `P-Gap = Breakout Gap`;
- exact wick/body treatment;
- exact `t-2` and `t` indexing as the canonical SP2L predicate;
- a minimum numeric gap size;
- a mandatory first-gap-of-move condition;
- a mandatory close-at-previous-high condition;
- the exact bearish mirror.

## Current hypothesis set

### H1 — Generic-gap identity

`P-Gap := High[t-2] < Low[t]` for bullish, with the bearish mirror still requiring direct source confirmation.

**Status:** strong candidate / not frozen.

### H2 — Generic gap + breakout context

The same three-candle relation plus the source-described Breakout-Gap context (gap at beginning of a move and associated close/location condition).

**Status:** strong candidate / not frozen.

### H3 — SP2L-specific P-Gap

A related but stricter predicate whose exact OHLC/sequence rule is not uniquely visible in the current source frames.

**Status:** unresolved; must remain open.

## Decision

Do not choose H1/H2/H3 using backtest performance. The raw source must resolve intended meaning before implementation.

No P-Gap production implementation is authorized.

## Next gate — Synthetic Fixtures

Proceed to fixtures that discriminate the hypotheses without deciding among them:

1. bullish three-candle wick gap where `High[t-2] < Low[t]`;
2. bullish body-only separation while wick extrema overlap;
3. generic gap plus Breakout-Gap close/location context;
4. overlap case where `High[t-2] >= Low[t]`;
5. adjacent-candle gap that does not satisfy the t-2 relation;
6. bearish mirror candidates;
7. equal-boundary case to test strict `<` versus non-strict `<=`.

Each fixture must use explicit OHLC values and expected outputs for each competing hypothesis. Fixtures are a geometry-disambiguation tool only; they do not establish source meaning.

## Gate impact

- Source Resolution: **BLOCKED at P-Gap executable geometry**
- Synthetic Fixtures: **NEXT**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**
