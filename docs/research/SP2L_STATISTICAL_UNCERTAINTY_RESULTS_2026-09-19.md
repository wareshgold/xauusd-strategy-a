# SP2L Statistical Uncertainty Results — 2026-09-19

## Sample
- Historical window: 2026-09-14 through 2026-09-18 UTC
- Total signals: 38
- Decisive: 37
- WIN: 27
- LOSS: 10
- AMBIGUOUS: 1 excluded from realized statistics

## Observed statistics
- Decisive win rate: 72.973%
- Wilson 95% CI: 57.022% to 84.603%
- Net: +643.4 accounting pip
- Net P/L at 0.01 lot: +$64.34
- Profit factor: 3.0675
- Average win / average loss: 1.1361

## Bootstrap — 20,000 resamples
| Metric | 95% percentile interval |
|---|---:|
| Win rate | 59.46% to 86.49% |
| Net pips | +235.59 to +1034.50 |
| Net P/L @ 0.01 lot | +$23.56 to +$103.45 |
| Profit factor | 1.466 to 8.347 |
| Average win/loss ratio | 0.780 to 1.660 |

Bootstrap median values:
- Win rate: 72.973%
- Net pips: +649.50
- Net P/L: +$64.95
- Profit factor: 3.124
- Average win/loss ratio: 1.153

## Largest-winner sensitivity
Removing the largest winning trades descriptively, without using the exercise for optimization:

| Removed largest wins | Remaining WR | Remaining Net pip | Remaining PF |
|---:|---:|---:|---:|
| 1 | 72.22% | +575.0 | 2.848 |
| 2 | 71.43% | +507.9 | 2.632 |
| 3 | 70.59% | +447.5 | 2.438 |
| 5 | 68.75% | +331.6 | 2.066 |

## Interpretation boundary
Within this historical sample, the bootstrap distributions for win rate, net pips, net P/L and profit factor remain above their zero/neutral profit boundary. The average win/loss ratio is less certain: its 95% bootstrap interval includes values below 1.

This is evidence of positive historical sample behavior, not proof of a production edge. The bootstrap treats trades as exchangeable and does not model temporal dependence. The window is not a fresh post-boundary holdout, and execution costs are not reconstructed.

The largest-winner sensitivity indicates that the positive historical result is not solely dependent on the five largest wins, but this remains a descriptive robustness check rather than a statistical guarantee.

## Gate impact
- Statistical uncertainty: DESCRIPTIVE POSITIVE EVIDENCE / LIMITED SAMPLE
- Parameter Robustness: POSITIVE research evidence
- Parameter Stability: INCONCLUSIVE — NO PASS / NO FAIL
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Frozen Geometry: BLOCKED
- Production: BLOCKED
- Live Trading: DISABLED

Research implementation: scripts/analyze-sp2l-statistical-uncertainty.py
Output artifact: artifacts/SP2L_statistical_uncertainty_2026-09-14_2026-09-18.json
Guard: RESEARCH STATISTICS ONLY; NO RULE OR PARAMETER PROMOTION.