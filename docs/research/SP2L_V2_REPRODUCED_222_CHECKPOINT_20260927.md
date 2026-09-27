# SP2L V2 — Reproduced 222 Reference Checkpoint — 2026-09-27

Status: RESEARCH FORENSICS — REFERENCE REPRODUCED — NOT CANONICAL

## Execution

The exact V2 MT5 runner was re-executed on the connected Otet Group MT5 terminal with:

- requested symbol: XAUUSD
- resolved symbol: XAUUSD.ecn
- timeframe: M1
- window: 2026-09-14T00:00:00Z through 2026-09-25T23:59:59Z
- explicit MT5 terminal path: C:\Program Files\Otet Group MT5 Terminal\terminal64.exe

Command:

```
.\.venv\Scripts\python.exe .\scripts\run_sp2l_strategy_a_v2_mt5_backtest.py --symbol "XAUUSD" --start "2026-09-14T00:00:00Z" --end "2026-09-25T23:59:59Z" --mt5-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"
```

Generated report:

`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260927T091652Z.json`

## Reproduced result

- signals: 222
- trades / decisive: 204
- wins: 127
- losses: 77
- decisive win rate: 62.254901960784316%
- net: +50R
- profit factor simplified: 1.6493506493506493
- max drawdown: 6R
- max consecutive losses: 5
- BUY: 94 trades, 59 wins, 35 losses, +24R
- SELL: 110 trades, 68 wins, 42 losses, +26R
- exits: 127 TP, 74 SL, 3 SL_FIRST_SAME_BAR

## Provenance conclusion

This reproduces the previously preserved 222 / 204 / 127 / 77 checkpoint exactly at aggregate level.

The reproduction uses the identified runner commit `a836ed038ae84a401b32dfc27690ddb04044de01` contract and detector blob `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`.

This establishes that the 222 checkpoint is reproducible under the current connected MT5 environment with the exact V2 runner contract.

## Important limitation

Aggregate equality does not prove signal-by-signal equality with the original 05:22Z artifact because that original JSON ledger is not currently available for hashing.

Therefore:
- the 222 result is now a reproducible reference checkpoint;
- the 227 dedicated baseline remains a separate execution/outcome contract;
- neither is canonical Strategy A;
- no geometry change is authorized from performance.

## Next gate

Freeze the reproduced 222 ledger and the 227 baseline ledger, then run multiplicity-preserving signal reconciliation. The comparison must separate:
1. signal population,
2. trigger/indexing,
3. geometry/config,
4. fill semantics,
5. outcome evaluator,
6. data acquisition.

No averaging, cherry-picking, or performance-based rule selection.
