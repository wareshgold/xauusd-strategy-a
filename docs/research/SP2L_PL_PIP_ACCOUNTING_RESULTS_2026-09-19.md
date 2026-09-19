# SP2L P/L & Pip Accounting Results — 2026-09-19

## Scope

Research-only accounting layer for the archived SP2L author-replica signal window:
- Window: 2026-09-14 through 2026-09-18 UTC
- Signals: 38
- Outcomes: 27 WIN, 10 LOSS, 1 AMBIGUOUS
- Symbol: XAUUSD.ecn
- Timeframe: M1

This measures historical price movement and broker-specific monetary value. It does not define, promote, or validate Strategy A geometry, entry, SL, TP, fill semantics, or execution rules.

## MT5 symbol economics

Acquired from the connected local MT5 terminal using scripts/mt5_xauusd_symbol_spec.py:
- digits: 2
- point: 0.01
- trade_tick_size: 0.01
- trade_tick_value: 1.00 account currency per 1.00 lot
- trade_tick_value_profit: 1.00
- trade_tick_value_loss: 1.00
- trade_contract_size: 100.00
- currency_profit: USD
- minimum volume: 0.01 lot
- volume step: 0.01

For this accounting view only, 1 pip is defined as 0.10 XAUUSD price units. This is a reporting convention, not a source-confirmed SP2L rule.

At 0.01 lot:
- 0.01 price unit = $0.01
- 0.10 price unit = 1 accounting pip = $0.10
- 1.00 price unit = $1.00

## Results

| Metric | Result |
|---|---:|
| Gross profit | +954.6 pip |
| Gross loss | -311.2 pip |
| Net | +643.4 pip |
| Gross profit @ 0.01 lot | +$95.46 |
| Gross loss @ 0.01 lot | -$31.12 |
| Net P/L @ 0.01 lot | +$64.34 |
| Profit factor | 3.0675 |
| Max historical sequential drawdown @ 0.01 lot | $7.58 |

The 1 ambiguous signal is excluded from realized P/L and pip totals because its outcome is SL_AND_TP_SAME_BAR and the archived artifact does not establish a canonical resolution semantics.

## Per-signal accounting artifact

Input: artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json

Output: artifacts/SP2L_pl_pip_accounting_2026-09-14_2026-09-18.json

Accounting inputs: pip size 0.10 price units; tick size 0.01; tick value $1.00 per 1.00 lot; accounting lot 0.01.

## Interpretation boundary

These results are descriptive historical accounting only.

They do not establish canonical P-Gap geometry, canonical AB=CD anchors or tolerance, canonical swing/SL anchor, canonical trigger touch/fill semantics, pending-order lifecycle, production execution rules, or live-trading authorization.

They also exclude commissions, swaps, slippage and other execution costs because those were not established by the archived signal artifact.

## Gate impact

- Source Resolution: PARTIAL
- Assumption Dependency: COMPLETE for the frozen candle-level window
- Frozen Geometry: BLOCKED
- Parameter Robustness: POSITIVE research evidence
- Parameter Stability: INCONCLUSIVE — NO PASS / NO FAIL
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Production: BLOCKED
- Live Trading: DISABLED

## Reproducibility

Accounting implementation: scripts/calculate-sp2l-pl-pip-accounting.py
MT5 symbol metadata acquisition: scripts/mt5_xauusd_symbol_spec.py

This report intentionally records broker economics separately from Strategy A source semantics.