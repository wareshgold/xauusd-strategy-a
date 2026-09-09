# SP2L F15 Bearish Mirror Run V1 — 2026-09-09

## Scope

F15 tests whether the source-aligned bullish SP2L sequence has a deterministic directional mirror. The fixture does not assume that every bullish detail automatically transfers to bearish execution.

## Tested mirror

Bullish:

Higher Lows → Breakout → P-Gap → Correction → Leg 2
→ Buy Limit
→ structural invalidation below structural low

Bearish candidate mirror:

Lower Highs → Breakout → P-Gap → Correction → Leg 2
→ Sell Limit
→ structural invalidation above structural high

## Result

**PASS — directional structural mirror preserved.**

The abstraction can represent the bearish counterpart without changing the order type into a market-reclaim model or inventing new price geometry.

## Important limitation

This fixture proves representability/symmetry of the abstract state machine only. It does **not** prove that every geometric detail, P-Gap definition, trigger form, entry anchor, stop anchor, 2X rule, or AB=CD construction is source-confirmed for bearish setups.

Those details remain unresolved until direct bearish source examples or stronger source evidence are resolved.

## Gate decision

**F15 SYNTHETIC MIRROR: PASS**

**SOURCE RESOLUTION: PARTIAL**

**FROZEN GEOMETRY: BLOCKED**

No bearish production detector is authorized solely from symmetry.

## Next step

Consolidate F02–F15 into a source-resolution blocker matrix and identify the minimum remaining visual/source questions required before Frozen Geometry.
