# SP2L Session Snapshot — 2026-09-15

## Status

**Official session checkpoint — RESEARCH / ENGINEERING ONLY**

This snapshot records the state at the end of the 2026-09-15 session so work can resume without reconstructing decisions from chat history.

## Project

Repository: `wareshgold/xauusd-strategy-a`

Project objective: build a source-aligned, deterministic, statistically validated XAUUSD Strategy A system based on SP2L (Spike → 2 Leg).

Governance remains:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Source meaning outranks backtest performance. No unresolved geometry is promoted to canonical rules. AI does not autonomously define canonical geometry or production BUY/SELL decisions.

## Strategy A source-resolution status

Current human-adjudicated baseline:

| Dimension | Current status |
|---|---|
| C01 P-Gap | `SOURCE_DISCRIMINATED` |
| C02 SL | `WORKING_FIXED_TEST_RULE` — initial SL 50/60/70/80 pips; RR 1:2 |
| C03 AB=CD / Leg-2 equality | `REMAINS_BLOCKED` |
| C04 TP1 / TP2 / 2X | `SOURCE_DISCRIMINATED` |
| C05 M15 / MA50 | `WORKING_FIXED_TEST_RULE` |
| C06 Pending-order behavior | `SOURCE_DISCRIMINATED` |
| C07 Trigger classifier | `REMAINS_BLOCKED` |
| C08 Correction / invalidation | `REMAINS_BLOCKED` |

These are not a frozen canonical Strategy A geometry package. The blocked dimensions remain blocked, and working experiment rules remain non-canonical.

## Current execution-layer work

MT5 trailing stop is being treated strictly as an **optional execution/position-management capability**, not as Strategy A geometry.

Current policy:

- trailing capability: planned;
- production: **OFF**;
- research baseline: **no trailing**;
- no trailing formula has been invented;
- no distance, activation threshold, step, tick/bar convention, or broker numeric constraint has been frozen;
- no MQL5 EA or live position modification has been implemented;
- favorable-only SL movement is an engineering safety invariant, not a source-derived Strategy A rule.

The execution skeleton includes deterministic boundaries for:

1. trailing disabled;
2. execution contract unfrozen;
3. broker constraints unavailable/incomplete;
4. invalid request;
5. unfavorable SL movement;
6. broker rejection;
7. accepted modification intent.

Synthetic BUY and SELL safety cases are intended to remain separate and deterministic.

## Important GitHub state

PR #196:

- title: `engineering: add MT5 position-management skeleton for optional trailing stop`
- state: OPEN
- draft: YES
- merged: NO
- mergeable: YES
- base: `main`
- branch: `research/mt5-trailing-stop-execution-2026-09-15`
- **GitHub currently reports PR head `a49fa5134336c0c9bb78bf3693afe13494da95c5`**.

The session identified that later trailing-related commits discussed in chat are not currently reflected by PR #196's GitHub-reported head. Therefore this is an explicit synchronization item for the next session.

## CI state

The last verified green execution-boundary CI was associated with commit `a49fa5134336c0c9bb78bf3693afe13494da95c5`, run `34970469722`.

For the later discussed trailing changes, no workflow run was found for commit `cf1234647f0da9ddde9dd8ddc63d0c82250dc8b6` at checkpoint time.

Therefore:

- do **not** claim the later changes are CI-verified;
- do **not** treat the earlier green run as validation of later commits;
- next session must synchronize the actual PR head and then validate CI on that exact head.

## Completed engineering concepts this session

- deterministic trailing-stop safety helper for favorable-only movement;
- Vitest conversion/fixes for trailing safety and position-manager tests;
- deterministic trailing execution state machine;
- broker constraint validation boundary;
- synthetic MT5 request contract;
- position-modification pipeline boundary;
- MT5 adapter/interface boundary;
- execution-layer documentation and implementation gates;
- explicit separation of trailing treatment from the no-trailing research baseline.

## Explicit non-decisions preserved

The project has **not** decided or invented:

- trailing distance;
- activation condition;
- step size;
- tick vs bar evaluation;
- exact broker stop/freeze distance semantics;
- spread policy;
- fill semantics;
- Strategy A P-Gap formula;
- entry geometry;
- AB=CD anchors/tolerance;
- trigger classifier;
- invalidation OHLC boundary;
- bearish mirror;
- production BUY/SELL rules.

## Next-session continuation order

1. Synchronize PR #196 with the actual latest intended execution-layer commits.
2. Verify exact PR head and workflow trigger.
3. Run/inspect Build and Test on the exact head.
4. Harden deterministic state-machine tests, including BUY/SELL and non-finite inputs.
5. Harden the end-to-end position-modification pipeline without introducing broker-distance formulas.
6. Keep the MT5 native adapter as a refusal-safe typed boundary until execution parameters are explicitly frozen.
7. Re-check that trailing remains OFF and separate from the research baseline.
8. Only after engineering validation, return to the governed research sequence.

## Stop point

**Session closed here.**

No merge, production activation, live execution, canonical geometry freeze, or BUY/SELL authorization is performed by this checkpoint.
