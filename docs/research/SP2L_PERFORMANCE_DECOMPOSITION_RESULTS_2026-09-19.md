# SP2L Performance Decomposition Results — 2026-09-19

## Input
- Window: 2026-09-14 through 2026-09-18 UTC
- Signals: 38
- Decisive: 37
- WIN: 27
- LOSS: 10
- AMBIGUOUS: 1
- Net decisive result: +643.4 accounting pips
- Accounting lot: 0.01
- Pip convention: 0.10 XAUUSD price units

## R-to-price accounting
| Metric | Result |
|---|---:|
| Average WIN | +35.36 pip |
| Median WIN | +31.40 pip |
| WIN range | +10.40 to +68.40 pip |
| Average LOSS | -31.12 pip |
| Median LOSS | -27.85 pip |
| LOSS absolute range | 12.20 to 75.80 pip |
| Average WIN / Average LOSS | 1.1361 |
| Net decisive result | +643.4 pip |

The observed historical result is produced by both win frequency and positive average win/loss magnitude ratio. This is descriptive only.

## Direction decomposition
BUY: 21 signals, 16 wins, 5 losses, 76.19% decisive WR, +456.3 pip net, +$45.63 at 0.01 lot, PF 3.664.
SELL: 16 signals, 11 wins, 5 losses, 68.75% decisive WR, +187.1 pip net, +$18.71 at 0.01 lot, PF 2.337.

Both directions contributed positive historical net pip totals. No direction is promoted, filtered, or preferred as a Strategy A rule.

## Sequential drawdown
- Maximum sequential drawdown at 0.01 lot: $7.58
- Occurred between decisive signal indices 24 and 25.
- This is an ordered historical drawdown calculation, not a complete broker-realized equity curve.

## Fixed-lot arithmetic scaling
| Lot | Net P/L | Max sequential DD |
|---:|---:|---:|
| 0.01 | +$64.34 | $7.58 |
| 0.05 | +$321.70 | $37.90 |
| 0.10 | +$643.40 | $75.80 |
| 0.50 | +$3,217.00 | $379.00 |
| 1.00 | +$6,434.00 | $758.00 |

This is linear arithmetic scaling of the same historical price outcomes. It is not a claim that these volumes are executable or appropriate.

## Accounting boundary
The 1 ambiguous signal is excluded from realized P/L because its outcome is SL_AND_TP_SAME_BAR and no canonical resolution semantics have been established.
Commissions, swaps, slippage, spread-at-fill, pending-order lifecycle, and broker execution mechanics are not reconstructed.

## Research interpretation
1. Positive result is not solely a high win-rate effect; average winning movement also exceeds average losing movement.
2. Both BUY and SELL contributed positive historical net pip totals in this window.
3. Fixed-lot scaling changes monetary exposure and drawdown linearly in this arithmetic model.
4. The sample remains small (37 decisive outcomes), so this does not establish a statistically validated production edge.
5. No canonical Strategy A rule is inferred or promoted.

## Gate status
- Source Resolution: PARTIAL
- Assumption Dependency: COMPLETE for frozen candle-level window
- Parameter Robustness: POSITIVE research evidence
- Parameter Stability: INCONCLUSIVE — NO PASS / NO FAIL
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Frozen Geometry: BLOCKED
- Production: BLOCKED
- Live Trading: DISABLED

Research analyzer: scripts/analyze-sp2l-performance-decomposition.py