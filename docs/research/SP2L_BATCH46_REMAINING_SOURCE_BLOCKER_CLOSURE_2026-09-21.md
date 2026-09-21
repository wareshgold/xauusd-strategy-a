# SP2L Batch 46 — Remaining Source Blocker Closure Pass
Date: 2026-09-21

## Objective
Advance the highest-value remaining source-resolution blockers in parallel after the F14 AB=CD closure attempt, without using backtest performance or implementation convenience to define canonical geometry.

## F14 — AB=CD
- Concept / magnitude relation: SOURCE-CONFIRMED.
- Leg2 is expected to approximately/effectively equal Leg1.
- A/B/C/D endpoints: UNRESOLVED.
- Price field and wick/body semantics: UNRESOLVED.
- D observed/projected semantics: UNRESOLVED.
- Equality tolerance: UNRESOLVED.
- No canonical AB=CD detector is permitted.

## F08/F10 — Swing and structural stop
Existing evidence supports treating the relevant swing / structural invalidation question as a source-discrimination problem, not a risk-optimization problem.
- F08 universal swing algorithm: UNRESOLVED.
- F10 exact structural OHLC anchor: UNRESOLVED.
- Wick/body/base/latest-opposite-swing alternatives remain explicit.
- Spread/buffer/minimum-distance substitutions are NOT canonical.
- User-reported teacher clarification that SL is under/over the SPIKE SHADOW plus spread remains evidence requiring archival/source verification; it does not by itself authorize a production rule.

## F11 — Pending refresh
- Pending Limit / refresh behavior is qualitatively source-supported.
- Exact delete predicate, timeout, replacement construction, and precedence: UNRESOLVED.
- No timeout or replacement threshold is frozen.

## F12/C07 — Trigger
- Source evidence supports a corrective/second-leg trigger family.
- Exact 1/2/3-candle taxonomy, indexing, activation boundary and precedence: UNRESOLVED.
- No canonical trigger classifier is frozen.

## F15 — Bearish mirror
- Synthetic bullish→bearish symmetry: PASS as a fixture property.
- Source-confirmed universal bearish OHLC geometry: UNRESOLVED.
- Synthetic mirroring cannot substitute for explicit bearish source evidence.

## F13/C04 — 2X
- 2X concept: SOURCE-CONFIRMED.
- Exact numeric semantics for second position / TP1 / TP2: UNRESOLVED.
- No universal half-target or R-multiple formula is frozen.

## Gate decision
This pass does NOT close Frozen Geometry.

| Gate | Status |
|---|---|
| Source Resolution | PARTIAL |
| P-Gap concept | SOURCE-CONFIRMED |
| P-Gap executable geometry | UNRESOLVED |
| F08 swing | UNRESOLVED |
| F10 structural stop | UNRESOLVED |
| F11 pending refresh | UNRESOLVED |
| F12 trigger taxonomy | UNRESOLVED |
| F13 2X numeric semantics | UNRESOLVED |
| F14 AB=CD anchors/tolerance | UNRESOLVED |
| F15 bearish source geometry | UNRESOLVED |
| Frozen Geometry | BLOCKED |
| Untouched Validation | LOCKED |
| Robustness/Stability | LOCKED |
| Fresh Holdout | BLOCKED |
| Production | BLOCKED / DISABLED |

## Next executable research sequence
1. Source-only F08/F10 closure attempt.
2. Source-only F11/F12 closure attempt in parallel.
3. Source-only F15 bearish evidence closure attempt.
4. Only after source discrimination: update frozen-geometry specification and synthetic fixtures.
5. Only after geometry freeze: untouched validation and fresh holdout.

## Prohibited actions
No backtest-selected anchors, tolerance optimization, invented P-Gap formula, guessed fill semantics, or canonical promotion from author implementation.
