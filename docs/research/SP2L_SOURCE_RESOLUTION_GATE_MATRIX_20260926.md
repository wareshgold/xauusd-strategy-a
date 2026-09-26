# SP2L Source Resolution Gate Matrix — 2026-09-26

## Purpose
This checkpoint consolidates source-resolution work through F15 into one deterministic gate matrix. Source meaning outranks backtest performance. A rule is not canonical merely because a research implementation produces favorable statistics.

## Global gate
**Frozen Geometry: BLOCKED**
**Untouched Validation: LOCKED**
**Robustness/Stability: LOCKED as a promotion gate**
**Fresh Holdout: LOCKED**
**Production BUY/SELL generation: OFF**

The current evidence supports several SP2L concepts, but does not yet bind all required OHLC anchors, trigger semantics, pending-order lifecycle, and execution semantics into one reproducible executable contract.

## Gate matrix

| Area | Source status | Confirmed | Still unresolved | Canonical eligible? | Gate effect |
|---|---|---|---|---|---|
| SP2L core concept | SOURCE-CONFIRMED | Spike -> 2Leg structure; second leg is a central completion concept | Exact executable geometry | No | Geometry remains blocked |
| P-Gap / Pressure Gap | SOURCE-CONFIRMED + SOURCE CEILING | Valid SP2L Spike requires a price gap/P-Gap; multiple structural orderings can qualify | Exact candle roles/indexing, pressure/trend qualification, minimum gap, precedence across variants | No | Do not promote a guessed formula |
| F10 stop anchor | SOURCE-PARTIAL / SOURCE CEILING | Stop/invalidation is structurally tied to spike-origin context; stop distance is known before activation | Exact wick/body/OHLC boundary, buffer, broker semantics | No | SL geometry unresolved |
| F11 pending lifecycle | SOURCE-PARTIAL | Pending Buy Limit exists; order can be refreshed/replaced when stop distance changes; pending can activate | Replacement threshold, sizing equation, cancellation, fill semantics, deterministic bearish lifecycle | No | Execution contract unresolved |
| F12 trigger acceptance | SOURCE-PARTIAL | Correction toward prior structural low/high; pending Limit; signal/key-bar confirmations; activation | Exact reference level, candle index, touch/cross/close, entry anchor, precedence, fill semantics | No | Entry trigger unresolved |
| F13 2X | SOURCE-PARTIAL / RELATION CONFIRMED | Optional secondary entry exists; later/closer-to-target relation; author material describes a 50%-of-entry-to-stop relationship | Exact price equation as executable rule, sizing, lifecycle, fill/cancel semantics, bearish mirror | No | 2X cannot be canonicalized |
| F14 AB=CD | SOURCE-CONFIRMED concept / geometry unresolved | Leg2 expected to match Leg1 magnitude; AB=CD conceptual analogy; candle-level treatment | A/B/C/D anchors, wick/body semantics, equality tolerance, TP projection semantics | No | TP/leg geometry unresolved |
| F15 bearish mirror | SOURCE-CONFIRMED concept / executable mirror unresolved | Direct bearish example; lower highs, upward corrections, Leg1 -> Correction -> Leg2, nested 2Leg | Exact bearish P-Gap, trigger, entry, SL, A/B/C/D, tolerance, 2X and execution semantics | No | Cannot derive mirror by code symmetry |

## Source-grounded concepts
1. SP2L is a Spike -> 2Leg framework.
2. A valid SP2L Spike requires a price gap/P-Gap; a sharp move without the required gap is not equivalent to the valid spike.
3. P-Gap can appear in more than one structural ordering around breakout/higher-lows/delayed formation.
4. Leg2 is expected to correspond to the magnitude of Leg1.
5. Pending Limit entry is part of the demonstrated workflow.
6. Pending orders can be refreshed/replaced when subsequent structure changes the stop-distance situation.
7. Signal-bar/key-bar confirmations are demonstrated as additional setup information.
8. An optional 2X position exists.
9. A bearish/downward SP2L construction is directly illustrated rather than being merely inferred by symmetry.

These are concept-level source facts, not permission to invent missing OHLC or execution semantics.

## Critical unresolved contract
- exact P-Gap candle mapping and qualification;
- exact stop/invalidation anchor;
- exact trigger reference and trigger semantics;
- exact entry-price anchor;
- pending-order replacement threshold and sizing;
- fill/touch/penetration semantics;
- exact A/B/C/D anchors;
- equality/tolerance for Leg1 = Leg2;
- exact TP/completion mapping;
- exact 2X price/sizing/lifecycle semantics;
- deterministic bearish execution mirror.

## Research implementation boundary
Existing research detectors, MT5 replays, forward-test runners, and parameter studies remain research artifacts unless and until their geometry is source-bound.

Do not promote historical candidate P-Gap formulas, a guessed universal Low[t] > High[t-2] SP2L formula, a fixed 2X half-distance formula solely from implementation convention, a wick/body/open/close stop anchor from backtest behavior, or a mechanically reversed bearish rule.

Do not select among unresolved geometries using win rate, PF, R, or holdout performance.

## Next source-resolution work
1. Primary visual/source escalation where original frames can bind exact candle/price roles.
2. If no new primary evidence exists, record a source ceiling rather than inventing a rule.
3. Keep discrimination fixtures frozen and reusable.
4. Only after every required canonical geometry field is source-bound may Frozen Geometry be reconsidered.
5. After geometry freeze, run untouched validation before robustness/stability promotion.
6. Fresh holdout remains reserved until the rule set is frozen.

## Non-negotiable decision rule
**Backtest performance cannot resolve source ambiguity.**
If two geometries remain source-equivalent or source-unresolved, both remain research hypotheses and neither becomes canonical.

## Checkpoint identity
- Date: 2026-09-26
- Latest completed source checkpoint: F15
- F15 commit: 2ddb7f1a14f842f3f7289cfaa94021ef8488ea10
- Matrix status: SOURCE RESOLUTION CONSOLIDATION
- Frozen Geometry: BLOCKED
- Production: OFF
