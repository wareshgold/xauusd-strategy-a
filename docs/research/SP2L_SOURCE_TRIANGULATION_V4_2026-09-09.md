# SP2L Source Triangulation V4 — 2026-09-09

## Scope

This phase triangulates the recovered authoritative transcript against direct frame inspection of the uploaded 01:09:15.667 source video. The purpose is to narrow source geometry without promoting ambiguous visual interpretations into production rules.

## Evidence set

- Authoritative transcript Git blob: `47f867385338738a23b2d06dc48e67b852127243`
- Source video: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- High-value transcript interval: 31:43–57:45
- High-value visual intervals: 36:20–40:20, 49:40–50:55, 55:00–57:35

## Finding 1 — P-Gap has two source-recognized temporal constructions

The transcript explicitly distinguishes:

1. breakout first, followed by follow-through and higher lows, with P-Gap in the breakout construction;
2. higher lows first, followed by the gap.

At 34:35–35:37 the teacher states that these two constructions are conceptually the same for the current SP2L strategy. A third three-candle construction is also included in the source Spike family.

### Decision

P-Gap must not be implemented with a universal fixed candle index. The source semantic is a breakout-associated pressure-gap condition whose location can occur at different points in the Spike construction.

Still unresolved:
- exact OHLC boundary pair;
- wick versus body;
- equality/touch rule;
- minimum size;
- whether every source Spike variant uses the same executable gap test.

## Finding 2 — Follow-through is independently source-defined

At 31:02–31:29 the source describes a valid breakout as a close beyond the prior level followed by a next candle that cannot return/overlap into the prior range. This is stronger than a generic breakout-only rule.

### Research contract

`breakout close beyond prior level + follow-through non-return/limited overlap`

must remain distinct from the P-Gap detector until the exact P-Gap boundary is resolved.

## Finding 3 — Spike is explicitly a multi-candle structural sequence

At 33:37–36:05 the teacher says the source strategy can treat three-candle directional constructions as one trend/Spike, and explicitly groups multiple constructions together. At 36:05 he summarizes the hierarchy of movement as Spike.

### Decision

Do not use a fixed candle count as the Spike definition. Candle count may be a source-example representation, but the canonical semantic is the directional structural movement after range/context.

## Finding 4 — First pullback / relevant prior Low is the strongest entry interpretation

At 38:38 the transcript states that when the next candle begins correction, correction means price comes below the first Low and the order can be placed there manually or as a pre-set limit. At 39:11 the order may already be placed within the initial three-candle construction. At 46:15 the teacher again describes three-candle opportunities where the next candle returns to the Low and the first pullback continues toward Leg 2.

The direct frames around 38:40–39:50 show a horizontal Limit/Buy Limit reference and later a separate SL below the lower structural region.

### Decision

Source semantics are frozen for research as:

`directional Spike -> correction to relevant prior Low/High -> pending Limit in Spike direction`

The exact executable price is still not frozen. Do not hard-code `i-1`, exact wick extreme, body edge, C, or a retracement percentage.

## Finding 5 — Entry and structural invalidation are distinct

The source repeatedly places Entry/Buy Limit above the structural invalidation area for bullish examples and the mirrored Entry/SL relationship for bearish examples. The transcript at 39:26 explicitly explains that returning to the lower structural area invalidates the scenario.

### Decision

Risk must be represented structurally:

`risk_price = abs(entry_price - structural_invalidation_price)`

The exact OHLC point of the structural invalidation remains unresolved.

## Finding 6 — Order refresh is conditional, but the threshold is qualitative

At 39:48–40:16 the teacher permits deleting/replacing the pending order after a new candle changes the distance to SL. If the change is not materially large, the order may be kept/moved; if it is large, a new order with a new position size is used.

### Decision

Order lifecycle is canonical semantics, but no numerical refresh threshold may be invented.

Research interface must therefore represent an unresolved policy state rather than silently selecting a percentage or price-distance threshold.

## Finding 7 — Leg 2 equality is source-confirmed, anchors are not

At 36:59–37:57 the source says the Spike should correct and complete a second leg equal to the first leg and explicitly names AB=CD. At 53:43 the teacher again explains that a pullback can return to the start of Leg 2 while preserving the broader leg structure.

### Decision

Freeze only:

`Leg2Magnitude ≈ Leg1Magnitude`

Do not freeze A/B/C/D as arbitrary swing points, entry price, breakout level, Fibonacci anchors, or any other imported convention.

## Finding 8 — TP1 is the teacher's preferred baseline; TP2 is explicitly an alternative

At 42:26–42:37 the source states TP1 and TP2 exist and that the teacher generally uses TP1 because TP2 is larger for this setup. At 42:48–43:11 the teacher explicitly instructs viewers to backtest the target behavior rather than accept the claim blindly.

### Decision

For research architecture:
- TP1 = source-preferred baseline management candidate;
- TP2 = separate candidate management module;
- exact TP1 geometry is not yet frozen;
- no optimization is authorized to select TP1/TP2 before source geometry is resolved.

## Finding 9 — Context/level and EMA60 are source usage, not yet universal Strategy A rules

At 43:21 onward the teacher discusses important levels, including round levels, and later at 49:47 explicitly uses EMA60 on M1 as contextual guidance. At 46:58–48:30 he also explains that SP2L can be added as a trigger to an existing context such as a channel or cycle.

### Decision

Do not promote `EMA60`, round levels, London/New York times, or a fixed session window into canonical SP2L rules merely because they appear in examples. They remain contextual/source-candidate filters requiring separate source-resolution evidence.

## Current deterministic research contract

The strongest source-aligned contract now is:

`context/range -> source-recognized directional Spike -> valid breakout + follow-through -> source-recognized P-Gap -> correction -> relevant prior Low/High -> pending Limit -> structural invalidation -> Leg2Magnitude approximately equals Leg1Magnitude`

with optional/separate management modules:

`TP1 / TP2 / 2X`

## Gate status

- SOURCE RESOLUTION: advanced
- SYNTHETIC DISCRIMINATION: complete/expanded
- FROZEN GEOMETRY: blocked
- DEV: locked
- UNTOUCHED VALIDATION: locked
- FRESH HOLDOUT: locked
- PRODUCTION: locked

## Explicit blockers

1. P-Gap exact boundary and timing rule.
2. Universal definition of relevant prior Low/High across all Spike variants.
3. Exact Entry price convention.
4. Exact structural SL OHLC anchor.
5. A/B/C/D candle-level anchors.
6. AB=CD numerical tolerance.
7. Exact TP1 geometry.
8. Deterministic pending-order refresh threshold.
9. Full mirrored bearish visual confirmation.

## Hard rule

No historical backtest, parameter sweep, or performance result may choose any of the unresolved interpretations above. If the source remains ambiguous, the implementation must retain an explicit unresolved state.
