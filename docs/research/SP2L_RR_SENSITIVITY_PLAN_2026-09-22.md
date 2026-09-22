# SP2L RR Sensitivity Research Plan — 2026-09-22

Status: RESEARCH ONLY

## Purpose

Evaluate the current research baseline's exit multiple without changing the signal
predicate, P-Gap candidate, SL candidate, or canonical geometry.

Baseline:
- P-Gap candidate: 1.0 price
- Spike multiplier: 1.5
- Max SL: 10 price
- SL candidate: spike/base structural extreme
- Current TP baseline: 1.0R
- Trailing stop: OFF
- Breakeven: OFF

## Tested TP multiples

The runner tests:
- 0.75R
- 1.00R
- 1.25R
- 1.50R
- 2.00R

For each snapshot it reports signal count, wins, losses, ambiguous and unresolved
outcomes, decisive win rate, total R, profit factor, and expectancy per decisive
trade.

## Interpretation rules

- No TP multiple becomes canonical from this sweep.
- A higher backtest result does not establish teacher/source fidelity.
- Results are descriptive until the source exit semantics are resolved.
- Trailing and breakeven are intentionally excluded from this baseline comparison
  so their effects can be studied separately without contaminating the RR study.
- Fresh holdout remains locked until the relevant geometry and research protocol
  are frozen.

## Next experiment

After the fixed-RR sensitivity is measured, run a separate research experiment
for trailing/breakeven variants. Do not combine RR selection and trailing
optimization in the same first sweep.
