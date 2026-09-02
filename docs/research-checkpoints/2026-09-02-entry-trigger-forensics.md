# Strategy A Research Checkpoint — 2026-09-02

## Branch
`research/volatility-hypothesis-holdout`

## Scope lock
- Research only.
- Do **not** modify production Strategy A rules/thresholds from this checkpoint.
- Do **not** mine the 5,000-candle fresh holdout for new hypotheses.
- Historical files are user-local modified assets; do not reset/checkout them.

## Current baseline
Strategy A deterministic chain:
`breakout → follow-through → spike → first correction → entry trigger → leg2 projection → invalidation → EMA/location/session context → quality → RR`

Baseline constants:
- BREAKOUT_LOOKBACK = 5
- FT_MAX_BARS = 2
- SPIKE_MAX_CANDLES = 8
- SPIKE_MIN_DIRECTIONAL_FRACTION = 0.50
- SPIKE_MAX_OVERLAP_FRACTION = 0.80
- EMA period = 60
- round step = 50
- round distance = 5
- LONDON = 07:00–16:00 UTC
- NEW_YORK = 13:00–22:00 UTC
- avoid windows = none

## Fresh holdout baseline
1m: n=163, winRate=20.86%, AvgR=-0.1815, PF=0.7707.
5m: n=138, winRate=28.26%, AvgR=+0.0536, PF=1.0747.

## Rejected hypotheses
- H1 entry-candle range / ATR14 >= 1.25: rejected on fresh holdout.
- Spike-strength hypothesis: rejected/unproven.
- Opportunity-window hypothesis: rejected.
- Entry-geometry single-factor hypotheses: rejected.
- Structural-chain quality filter: rejected.
- Temporal/regime stability: rejected.
- Strong/weak attribution: diagnostic only; no production filter.
- Frozen 5m SELL + NEW_YORK: H2 DEV/VAL passed and fresh holdout confirmed (n=28, AvgR=+1.4258, PF=3.3484), but dedicated 6-window robustness was FRAGILE_REJECT (3/6 positive, final window negative). Therefore **not a production filter**.

## Last invalid experiment
`research:entry-trigger-mechanics` reconstructed baseline entries after the fact and produced only 4 matched trades out of 210 on 5m, including a 694-bar loser delay. This is considered invalid for inference. No conclusions were taken from it.

## Correct next research direction
Instrument/replay the **actual baseline decision path candle-by-candle**, rather than reverse-engineering completed trades. Measure:
1. stage funnel counts;
2. exact rejection reasons;
3. correction → trigger latency;
4. correction depth;
5. trigger extension;
6. projection/invalidation/RR failures;
7. accepted-entry path descriptors.

The instrumentation must use only candles visible at each decision index and must not alter production logic.

## New research artifact
`scripts/analyze-baseline-entry-path-forensics.mjs`

Command:
`npm run research:entry-path-forensics`

Output directory:
`data/reports/strategy-a-entry-path-forensics/`

This is research-only and intentionally does not change `src/domain/strategy-a` or `run-baseline-backtest.ts`.

## Git commits since the last checkpoint
- `fa1bf2970ba48742a0dd948c1f3bb2ab46405278` — fixed entry-trigger mechanics premature break.
- `4eba96d8fc7d2154729143c30d8c903eb0908b6a` — added direct baseline path forensics script (initial).
- `a9d653a61a0b146cfc4463940655b6211aa53a13` — made the forensics script runnable as ESM.
- `5150e081feaca3b965bfdaef0bb4b4429b5eb33b` — added `research:entry-path-forensics` npm command.
- this checkpoint commit records the research state and next-step methodology.

## Important interpretation rule
The next run is a **diagnostic validation of the replay/instrumentation**, not a strategy optimization. First verify that the direct path reproduces baseline trade count/entry indices closely. Only after parity is established should any entry/trigger descriptor be investigated.
