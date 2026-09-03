# Strategy A Research Checkpoint — 2026-09-03

## Git checkpoint
- Repository: `wareshgold/xauusd-strategy-a`
- Working research branch: `research/outcome-stop-stress`
- Checkpoint commit: `68f331ee8ecc1573271d30bb19d845af3f675979`
- Purpose: preserve the current Outcome Path / Stop Stress investigation state before continuing research.

## Core project target
- Deterministic XAUUSD price-action strategy.
- Initial target RR: 1:2.
- Desired robustness target: WR >60% good, >70% better, >80% excellent.
- Minimum validation target also considers positive expectancy, PF, drawdown, loss streaks, and stability across time/session splits.
- Trading scope: London open through end of New York. Australia/Japan coverage is not required.
- MT5 Risk-Free automatic management is a later, separate layer; it must not be mixed into core entry-edge validation.
- No production Strategy A changes until a robust edge is demonstrated.

## Current baseline fresh-holdout status
Fresh holdout = last 5,000 candles; it remains untouched by the current research.

### 1m
- n=163
- AvgR=-0.1815
- PF=0.7707
- BUY AvgR=-0.4339, PF=0.462
- SELL AvgR=+0.1147, PF=1.148
- London AvgR=-0.4044, PF=0.516
- NY AvgR=+0.0662, PF=1.089

### 5m
- n=138
- AvgR=+0.0536
- PF=1.0747
- BUY AvgR=-0.2205, PF=0.705
- SELL AvgR=+0.3800, PF=1.557
- London AvgR=-0.4592, PF=0.388
- NY AvgR=+0.6741, PF=1.970

Conclusion: Strategy A is not ready for real-money trading.

## Research findings already rejected
- Fresh H1 volatility filter: rejected.
- Spike hypothesis: rejected on 1m; unproven on 5m.
- Opportunity-window hypothesis: rejected.
- Entry-geometry hypotheses: rejected on fresh holdout.
- Structural-chain hypothesis: rejected.
- Temporal stability hypothesis: rejected.
- Frozen SELL + New York direction/session filter: failed robustness despite strong 5m fresh result; no production filter.
- Candidate-count single-vs-multi hypothesis: rejected in DEV/VAL.
- Stop/first-correction geometry as a general production filter: rejected in DEV/VAL.
- Entry-trigger mechanics such as triggerDelay<=1 and stopToImpulse 25–50%: looked promising preholdout but failed fresh 5m holdout; do not promote.

## Important diagnostic observations
- 5m DEV/VAL baseline flips from AvgR +0.2575R to -0.1963R despite several path/structure medians being fairly stable.
- Outcome path analysis suggests opportunity may exist while adverse excursion/stop timing remains hostile, but OHLC same-candle ambiguity is substantial.
- Same-bar threshold ordering is often large enough that intrabar order cannot be inferred from OHLC.
- Candidate competition suggested the multi-candidate regime is weaker, but best alternative hindsight outcomes were also negative; candidate selection is unlikely to be the core failure.

## Latest stop-stress result
The diagnostic stop-stress replay kept canonical TP1 and varied the hypothetical stop distance.

### 5m
- 0.5x: DEV AvgR +1.1613 / PF 3.846; VAL AvgR -0.1498 / PF 0.648
- 0.75x: DEV +0.6621 / PF 2.144; VAL -0.0918 / PF 0.841
- 1.0x: DEV +0.2575 / PF 1.358; VAL -0.1963 / PF 0.727
- 1.25x: DEV +0.1502 / PF 1.181; VAL -0.4072 / PF 0.529
- 1.5x: DEV -0.0469 / PF 0.950; VAL -0.4795 / PF 0.517
- 2.0x: DEV -0.4661 / PF 0.611; VAL -0.8620 / PF 0.324

### 1m
- 0.5x: DEV AvgR -0.1819 / PF 0.590; VAL +0.2933 / PF 1.666
- 0.75x: DEV -0.2304 / PF 0.633; VAL +0.3550 / PF 1.585
- 1.0x: DEV -0.3564 / PF 0.555; VAL +0.0361 / PF 1.047
- 1.25x: DEV -0.5266 / PF 0.449; VAL -0.2351 / PF 0.749
- 1.5x: DEV -0.7703 / PF 0.320; VAL -0.3606 / PF 0.662
- 2.0x: DEV -1.1282 / PF 0.229; VAL -0.7177 / PF 0.460

Conclusion: widening the stop does not solve the 5m VAL problem; stop-too-tight is not supported as the general explanation. No production stop change.

## Known bug to fix before trusting threshold-ordering output
`analyze-outcome-stop-stress.mjs` currently has a sign/definition issue in the printed favorable/adverse threshold ordering section. The `A=0.0%` output is therefore not trustworthy and must not be used for conclusions. The stop-stress AvgR/PF replay is a separate diagnostic and remains useful.

## Immediate next step
1. Fix the adverse-threshold sign/definition bug in `scripts/analyze-outcome-stop-stress.mjs`.
2. Re-run the diagnostic without touching the fresh holdout.
3. Implement/verify an Outcome Survival Matrix using thresholds approximately ±0.25R, ±0.5R, ±0.75R, ±1R, ±1.5R, ±2R, ±3R across multiple horizons.
4. Compare DEV vs VAL for favorable/adverse reach rates, ordering, time-to-threshold, and outcome conditional on path class.
5. Decide whether the evidence points to entry quality, path timing, or management geometry.
6. Only after a hypothesis passes robust DEV/VAL checks should a one-time fresh-holdout test be considered.

## Guardrails
- Fresh 5,000-candle holdout remains reserved.
- No opportunistic production filters.
- No optimization toward the target win-rate numbers.
- No MT5 risk-free management mixed into the core edge test.
- No AI-generated discretionary BUY/SELL decisions.
