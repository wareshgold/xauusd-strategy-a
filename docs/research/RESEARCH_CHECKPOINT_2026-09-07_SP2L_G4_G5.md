# Research Checkpoint — 2026-09-07 — SP2L G4/G7

## Branch
`research/phase12-preentry-geometry-robustness`

## Authoritative synchronization
`docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`

Raw Poorsamadi source remains semantic authority. Deterministic definitions not uniquely established by source remain `CANDIDATE`; missing geometry remains `TBD`.

## Completed research foundation
- Phase32 semantic-state foundation validated.
- G1/G2/G3 research-only candidates and tests validated.
- G4/G5 source review completed as far as preserved text permits.
- G6 semantic equality relationship documented.
- G7 simulator/execution semantics documented separately from teacher semantics.
- Production Strategy A unchanged.

## G4 — Leg 1
Status: `SEMANTIC CORE SOURCE-CONFIRMED / EXACT A-B TBD / VISUAL SOURCE REQUIRED`.

The source establishes distinct Leg1 and Leg2 and their approximate equality, but transcript text does not encode the exact visual A/B chart coordinates. Candidate endpoint families remain separate; none is promoted by backtest performance.

Reference: `PHASE_33_G4_LEG1_SOURCE_RESOLUTION.md` and `PHASE_34_SP2L_G4_SOURCE_ANCHOR_2026-09-07.md`.

## G5 — Leg 2 origin
Status: `LEG1 -> CORRECTION -> LEG2 SOURCE-CONFIRMED / EXACT C TBD / VISUAL SOURCE REQUIRED`.

Candidate C origins remain correction extreme, actual fill, structural reference, or source-defined visual point. No candidate is promoted by PnL.

Reference: `PHASE_33_G5_LEG2_PROJECTION_ORIGIN_RESOLUTION.md`.

## G6 — Equality
Status: `SEMANTIC RELATION SOURCE-CONFIRMED / NUMERICAL TOLERANCE TBD`.

```text
abs(Leg2) ~= abs(Leg1)
```

No arbitrary percentage, ATR multiple, tick band, or historical-fitted tolerance has been introduced.

Reference: `PHASE_33_G6_LEG2_EQUALITY_SEMANTICS.md`.

## G7 — Execution
Status: `SEMANTIC LIFECYCLE SOURCE-CONFIRMED / SIMULATOR ORDERING POLICY EXPLICITLY SEPARATED`.

Pending-limit-before-fill, structural invalidation, fixed stop concept and TP1 are source-backed. Same-candle intrabar ordering, spread/slippage and exact event ordering are simulator policies and remain separate from teacher semantics.

Reference: `PHASE_33_G7_SP2L_EXECUTION_SEMANTICS.md`.

## Required gate before historical validation
1. Resolve visual A/B/C geometry from source material.
2. Build deterministic positive/negative synthetic fixtures for the frozen geometry.
3. Freeze G6 research tolerance only with explicit provenance; never attribute an invented band to Poorsamadi.
4. Validate G7 execution policy on fixtures, including same-candle ambiguity.
5. Only then run chronological DEV -> untouched VAL -> robustness.
6. Fresh Holdout remains locked until DEV/VAL survival.

## Hard constraints
- No production Strategy A changes.
- No historical result used to infer teacher meaning.
- No threshold mining.
- No VAL/Fresh optimization.
- No Fresh Holdout while core geometry is unresolved.
- No AI-generated BUY/SELL decisions.

## Continuation
If visual source frames become available, resolve G4/G5 directly. If not, keep those geometry fields `TBD`; do not invent them.
