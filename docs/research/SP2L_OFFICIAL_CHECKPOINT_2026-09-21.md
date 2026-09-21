# SP2L Strategy A — Official Progress Checkpoint — 2026-09-21

## Purpose

Official continuity checkpoint for the work completed on 2026-09-21.
This document is a research-state snapshot, not a canonical Strategy A specification.

## Repository / branch

- Repository: wareshgold/xauusd-strategy-a
- Branch: research/sp2l-f13-demo-forward-slfixed-2026-09-21
- PR: #259
- Strategy status: research-only
- Canonical BUY/SELL generation: disabled
- Production: disabled

## Source-resolution state

Frozen Geometry remains **BLOCKED**.

Resolved / source-aligned progress:
- P-Gap concept and adjacent-candle non-overlap primitive reconstructed from source evidence.
- P-Gap qualification remains incomplete: exact indexing, minimum gap, sequence precedence, early-trend/E-Gap boundary and universal executable qualification unresolved.
- F08 Swing: source meaning reconciled; deterministic pivot/window and wick/body endpoint unresolved.
- F09 Entry: source-shaped families covered; exact entry price field and trigger precedence unresolved.
- F10 Stop: source confirms stop is behind the candle from which the spike originated; exact field, buffer and invalidation event unresolved.
- F11/F12 execution: pending-order usage/lifecycle is source-shaped, but touch/breach/close/fill, timeout, activation and replacement semantics remain unresolved.
- F13 2X: Entry-to-SL midpoint relation is source-confirmed; lifecycle, sizing/risk aggregation and shared TP/SL behavior remain unresolved.
- F14 AB=CD: structural swing-to-swing interpretation is source-supported, but exact A/B/C/D endpoints and numerical tolerance remain unresolved.
- F15 bearish: geometry is source-consistent but independent executable bearish evidence remains incomplete.

## Research infrastructure completed

Synthetic fixture and discrimination coverage has been added for:
- P-Gap reconstruction and P-Gap/E-Gap context.
- Leg-1 boundary and anchor hypotheses.
- F08 swing source-resolution and counterexamples.
- F09/F14 dependency discrimination.
- F10 stop source-resolution and counterexamples.
- F11/F12/F13 execution discrimination.
- F14 AB=CD anchor families.
- Bearish geometry.
- Geometry dependency and resolution priority.
- Resolution coverage audit.
- Blocker-resolution plan.
- P0 source discrimination/counterexample discrimination.

No unresolved geometry has been promoted to canonical status.

## F10 research case study

Archived case:
- Entry: 4346.90
- Research SL: 4344.87
- Risk: 2.03
- TP at 1R: 4348.93
- SL anchor: SPIKE_CANDLE_EXTREME_RESEARCH
- Execution mode: PENDING_LIMIT_RESEARCH

Six-hour MT5 M1 observation:
- bars: 360
- high: 4383.42
- low: 4345.80
- last: 4351.79

The 50/60/70/80-pip alternatives were recorded only as counterfactual research comparisons. They are not canonical rules.

## Telegram / forward-monitor infrastructure

Telegram configuration has been verified in the local environment:
- Chat ID configured: -1004342109034
- Bot token presence verified without exposing the secret.
- Monitor script: scripts/telegram_forward_monitor.py
- Monitor mode: research-only reporting
- Symbol: XAUUSD.ecn
- Magic: 26091901
- Poll interval: 3 seconds
- Deal outcome reporting is infrastructure only and does not generate strategy decisions.

## Clean forward-test state

Current research branch configuration:
- pGapPrice: 1.0
- spikeMultiplier: 1.5
- maxSlDistance: 10
- tpR: 1
- volume: 0.01
- slAnchor: SPIKE_CANDLE_EXTREME_RESEARCH
- demoOrderMode: PENDING_LIMIT_RESEARCH

At checkpoint time:
- Forward runner started successfully.
- Telegram outcome monitor started successfully.
- Both are research-only / non-canonical.
- Only one clean forward-test instance should remain active.
- The previously recorded old forward-test evidence remains untouched.
- No historical result should be retroactively mixed into the new clean forward test.

## CI note

The Telegram monitor commit was checked for workflow status; no workflow run was exposed for that commit, so it is not labelled CI-green.

## Continuation rule

Future work must continue from this checkpoint rather than resetting to day 0.

Next research priorities:
1. Continue source resolution of P0 blockers F08 and F10.
2. Resolve dependent F09/F14 only after their upstream constraints are sufficiently resolved.
3. Continue F11/F12 execution semantics and F13 lifecycle discrimination.
4. Preserve clean forward-test evidence separately from historical/research backtests.
5. Do not promote rules to canonical or production from backtest/forward performance.

## Audit guardrail

Backtest performance does not override source meaning.
Unresolved geometry remains unresolved.
AI-assisted implementation is research infrastructure only and cannot autonomously define canonical Strategy A rules or production BUY/SELL decisions.
