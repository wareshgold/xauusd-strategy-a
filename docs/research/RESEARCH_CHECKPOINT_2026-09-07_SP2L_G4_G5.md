# Research Checkpoint — 2026-09-07 — SP2L G4/G5

## Branch
`research/phase12-preentry-geometry-robustness`

## Current authoritative synchronization map

`docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`

This map is the current research synchronization point. Raw Poorsamadi source remains semantic authority. Any deterministic definition not uniquely established by source remains `CANDIDATE`; missing geometry remains `TBD`.

## Current research state
- Phase32 semantic-state foundation is completed and validated.
- G1/G2/G3 structural geometry candidates are implemented as research-only candidates and their tests passed.
- G4 source review is complete as far as the text transcript allows; exact Leg1 A/B endpoints remain unresolved and require visual source evidence.
- G5 source review is now documented separately; semantic ordering `LEG 1 -> CORRECTION -> LEG 2` is source-confirmed, while the exact projection-origin C coordinate remains unresolved and requires visual source evidence.
- No canonical G4/G5 calculator has been promoted.
- Production Strategy A remains unchanged.

## Validation completed
- SP2L Semantic State: 12/12 tests passed.
- G1 Structural Reference: 3/3 tests passed.
- G2 Pending Limit: 5/5 tests passed.
- G3 Structural Stop: 4/4 tests passed.
- TypeScript build/type-check passed at the last implementation checkpoint.

## G1/G2/G3 candidate conclusions
- G1: bullish candidate uses previous relevant candle low / HL level; bearish candidate uses previous relevant candle high / LH level. This remains `CANDIDATE`, not source-confirmed as one universal structural algorithm.
- G2: bullish pending Buy Limit candidate = selected HL price; bearish pending Sell Limit candidate = selected LH price; activation is exact retest/touch. Pending-limit semantics are source-established, but the exact universal level mapping remains `CANDIDATE`.
- G3: bullish structural SL candidate = spike-origin low; bearish structural SL candidate = spike-origin high. Structural invalidation is source-established; the exact universal stop level remains `CANDIDATE`. No historical buffer optimization or invented buffer.

## G4 — Leg 1 source resolution
Status: `SEMANTIC CORE SOURCE-CONFIRMED / EXACT ENDPOINTS TBD / VISUAL SOURCE REQUIRED`.

Source confirms the SP2L relationship `Leg 2 ~= Leg 1`, but the transcript text does not expose exact chart coordinates for the endpoints of Leg 1. Candidate endpoint definitions must therefore NOT be selected from the transcript by guesswork or from historical outcomes.

Candidate families kept separate for future evidence:
1. structural low/high -> spike extreme
2. breakout -> spike extreme
3. spike start -> spike end
4. relevant open -> spike extreme
5. structural -> structural
6. source-defined visual A/B points

No historical optimization or canonical calculator has been built for G4.

Reference: `docs/research/PHASE_33_G4_LEG1_SOURCE_RESOLUTION.md`.

## G5 — Leg 2 projection origin
Status: `SEMANTIC ORDERING SOURCE-CONFIRMED / EXACT ORIGIN TBD / VISUAL SOURCE REQUIRED`.

Source establishes:

```text
LEG 1 -> CORRECTION -> LEG 2
```

The transcript does NOT uniquely establish that the exact C/projection origin equals the correction extreme, fill price, or structural reference.

Candidate origins remain separate:
1. correction extreme
2. actual fill
3. structural reference
4. source-defined visual chart point

G5 must not be promoted by backtest performance.

Reference: `docs/research/PHASE_33_G5_LEG2_PROJECTION_ORIGIN_RESOLUTION.md`.

## Required visual evidence for G4/G5

Highest-value source frames:
- 36:59–37:22
- 1:02:41–1:03:32
- 1:04:00–1:04:32

These are needed to resolve the actual visual A/B/C coordinates faithfully.

## Next steps
1. Obtain/inspect visual source evidence for the G4/G5 timestamps above.
2. Resolve one geometry question at a time without PnL-based semantic selection.
3. Once A/B/C geometry is source-resolved, create deterministic positive/negative synthetic fixtures.
4. Then address G6 equality tolerance without inventing a Poorsamadi percentage band.
5. Then freeze G7 execution/simulator semantics: limit touch/fill, SL/TP touch, same-candle ambiguity, spread/slippage and order-create/fill ordering.
6. Only after the complete candidate is frozen: chronological DEV -> untouched VAL -> robustness.
7. Only after DEV/VAL survival may Fresh Holdout be considered.

## Hard constraints
- Raw Poorsamadi source is semantic authority.
- Current Knowledge Map V2 is the synchronization map, not a license to fill TBDs.
- Fresh Holdout remains LOCKED.
- Production Strategy A remains untouched.
- No EMA50/100 promotion.
- No threshold mining.
- No VAL/Fresh optimization.
- No historical result is allowed to decide source meaning.
- Existing Strategy A close-reclaim / LegProjection behavior is implementation evidence only, not teacher intent.
- AI does not generate BUY/SELL decisions.

## Continuation instruction for next chat
Start from this checkpoint and `STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`. Inspect the raw source and G4/G5 resolution documents before changing geometry. Do not ask for the text transcript again; it is already stored in GitHub. If visual frames are available, use them to resolve A/B/C. If they are not available, keep G4/G5 `TBD` rather than inventing a rule.