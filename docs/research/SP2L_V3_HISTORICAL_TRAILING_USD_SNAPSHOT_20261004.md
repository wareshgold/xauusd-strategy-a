# SP2L V3 Historical Trailing Matrix — Fixed 0.01 Lot USD Snapshot

**Snapshot date:** 2026-10-04  
**Repository:** wareshgold/xauusd-strategy-a  
**Branch:** research/sp2l-v3-forward-reconciliation-20261003  
**Status:** RESEARCH / DIAGNOSTIC — NOT CANONICAL / NOT PRODUCTION

## Scope

This snapshot records the current historical trailing-matrix results after converting price movement to fixed-lot XAUUSD P&L for **0.01 lot**, using the project assumption that a 1.00 XAUUSD price move is approximately $1.00 at 0.01 lot (contract size 100).

Source matrix artifact:
- SP2L_V3_HISTORICAL_TRAILING_MATRIX_20261004T085652Z_COMBINED.csv
- SP2L_V3_HISTORICAL_TRAILING_MATRIX_20261004T085652Z_TRADES.csv

Windows:
- 1M: 2026-08-26 through 2026-09-25
- 3M: 2026-07-01 through 2026-10-01

## Critical exit interpretation

The leading configuration is **RR2_ACT0_TRAIL2_2XOFF**.

For this configuration in the 3M trade ledger:
- TRAIL_SL: 1476
- SL: 3
- AMBIGUOUS_SAME_BAR: 68
- TP: 0
- Total: 1547

Therefore the fixed-lot deterministic USD table excludes the 68 AMBIGUOUS_SAME_BAR trades and contains **1479 deterministic trades**.

The observed maximum deterministic profit of approximately **+$15.48** is **not a 2R TP**. A representative best trade was:

- Direction: SELL
- Entry: 4296.66
- Initial SL: 4306.02
- Initial risk: 9.36 price units
- RR2 TP level: 4277.94
- Final trailing SL: 4281.18
- Exit reason: TRAIL_SL
- Profit: +15.48 price units ≈ +$15.48 at 0.01 lot
- Realized result: +1.6538R
- Max favorable move: 15.50

Thus RR2 is present as the configured TP ceiling, but in this configuration the trade exited via trailing before reaching the RR2 TP. In the 3M ledger, no deterministic trade exited by TP.

## Current fixed-0.01-lot USD results

### 3M — top observed configurations

| Method | Deterministic trades | Net USD | Avg USD | Min USD | Max USD |
|---|---:|---:|---:|---:|---:|
| RR2_ACT0_TRAIL2_2XON | 1479 | +2683.88 | +1.8147 | -5.39 | +15.48 |
| RR2_ACT0_TRAIL2_2XOFF | 1479 | +2683.88 | +1.8147 | -5.39 | +15.48 |
| RR2_ACT5_TRAIL2_2XOFF | 1479 | +2670.91 | +1.8059 | -5.39 | +15.48 |
| RR2_ACT5_TRAIL2_2XON | 1479 | +2670.91 | +1.8059 | -5.39 | +15.48 |
| RR2_ACT0_TRAIL3_2XOFF | 1479 | +2669.12 | +1.8047 | -5.39 | +15.47 |
| RR2_ACT0_TRAIL3_2XON | 1479 | +2669.12 | +1.8047 | -5.39 | +15.47 |
| RR2_ACT10_TRAIL2_2XOFF | 1479 | +2663.97 | +1.8012 | -5.39 | +15.48 |
| RR2_ACT10_TRAIL2_2XON | 1479 | +2663.97 | +1.8012 | -5.39 | +15.48 |
| RR2_ACT15_TRAIL2_2XOFF | 1479 | +2659.84 | +1.7984 | -5.39 | +15.48 |
| RR2_ACT15_TRAIL2_2XON | 1479 | +2659.84 | +1.7984 | -5.39 | +15.48 |

### 1M — top observed configurations

| Method | Deterministic trades | Net USD | Avg USD | Min USD | Max USD |
|---|---:|---:|---:|---:|---:|
| RR2_ACT0_TRAIL2_2XON | 531 | +945.69 | +1.7810 | -4.00 | +15.48 |
| RR2_ACT0_TRAIL2_2XOFF | 531 | +945.69 | +1.7810 | -4.00 | +15.48 |
| RR2_ACT5_TRAIL2_2XOFF | 531 | +942.60 | +1.7751 | -4.00 | +15.48 |
| RR2_ACT5_TRAIL2_2XON | 531 | +942.60 | +1.7751 | -4.00 | +15.48 |
| RR2_ACT0_TRAIL3_2XOFF | 531 | +940.39 | +1.7710 | -4.00 | +15.47 |
| RR2_ACT0_TRAIL3_2XON | 531 | +940.39 | +1.7710 | -4.00 | +15.47 |
| RR2_ACT5_TRAIL3_2XON | 531 | +937.31 | +1.7652 | -4.00 | +15.47 |
| RR2_ACT5_TRAIL3_2XOFF | 531 | +937.31 | +1.7652 | -4.00 | +15.47 |
| RR2_ACT10_TRAIL2_2XON | 531 | +937.20 | +1.7650 | -4.00 | +15.48 |
| RR2_ACT10_TRAIL2_2XOFF | 531 | +937.20 | +1.7650 | -4.00 | +15.48 |

## Interpretation

The current evidence shows a very strong historical USD result for very tight trailing distances, especially ACT0/TRAIL2, and the result remains positive in both the nested 1M and 3M windows.

However, this is **not yet evidence of a production edge**.

Known limitations:
1. 1M is nested inside 3M; it is a stability check, not independent validation.
2. M1 high/low replay cannot resolve intrabar order. AMBIGUOUS_SAME_BAR trades are therefore excluded rather than guessed.
3. Trailing activation/update mechanics on an M1 bar can still contain an intrabar-ordering assumption and require explicit forensic validation.
4. 2X sizing/entry semantics remain source-sensitive; 2X ON/OFF equality in the current USD aggregation must not be interpreted as proof that 2X is irrelevant.
5. No canonical Strategy A rule has been changed by this snapshot.
6. No production BUY/SELL decision is implied.

## Current research conclusion

**Current leading diagnostic candidate:** RR2_ACT0_TRAIL2_2XOFF / ON.

**Current observed fixed-lot result:** approximately +$2,683.88 over the 3M deterministic subset and +$945.69 over the 1M deterministic subset.

**Interpretation:** promising research evidence, not validated strategy proof.

Next required research step is a trade-level forensic/stability audit of the leading trailing configurations, with explicit treatment of ambiguous bars and trailing mechanics before any promotion or fresh holdout.

