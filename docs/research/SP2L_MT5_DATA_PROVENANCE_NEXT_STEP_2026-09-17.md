# SP2L MT5 Data Provenance — Next Step (2026-09-17)

## Purpose

The production target for Strategy A is the MetaTrader 5 execution environment. TwelveData remains a research comparison feed only.

## Current evidence

- TwelveData XAU/USD M1 sample: 10,000 candles; the current author-replica candidate produced 0 full setups at the reported configuration.
- OTET MT5 export: symbol `XAUUSD.ecn`, M1, 10,000 candles; artifact replay produced 49 signals, 46 decisive outcomes, 2 ambiguous outcomes, 31 wins and 15 losses (`67.39%` decisive win rate, `+16R`, PF `2.07`).
- The OTET result is research-only and is not evidence that canonical Strategy A geometry has been frozen or validated.
- The existing Node runner named `run-author-replica-mt5-direct.mjs` replays the committed MT5-export JSON; it does not itself call the MT5 API.

## Direct-MT5 reproducibility step

`run-author-replica-mt5-api.py` has been added as a research-only runner. It uses `MetaTrader5.initialize()`, selects the configured symbol, calls `copy_rates_from()` for M1 bars, and applies the documented author-associated replica candidate without placing trades.

Default symbol: `XAUUSD.ecn`

Default sample size: `10,000`

Default data request mirrors the author implementation's documented `now UTC + 3 hours` provenance behavior.

## Required local run

```powershell
python scripts\run-author-replica-mt5-api.py
```

The next comparison must check:

1. returned bar count;
2. first/last UTC timestamps;
3. OHLC sequence compatibility with `artifacts/mt5_xauusd_m1_10000.json`;
4. signal count and signal timestamps;
5. win/loss/ambiguous accounting.

No P-Gap threshold, spike multiplier, fill semantics, AB=CD anchors, Round Level rule, or canonical geometry is to be changed to improve the observed result.

## Gate status

Source Resolution: PARTIAL PASS.

Frozen Geometry: BLOCKED.

Untouched Validation: LOCKED.

Robustness/Stability: LOCKED.

Fresh Holdout: LOCKED.

Production: OFF.
