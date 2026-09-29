# V2 Forward Test Launch Checkpoint — 2026-09-29

## Reference

Historical research artifact:
`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_MT5_20260928T074842Z.json`

Reference result:
- signals: 1,472
- trades: 1,356
- wins: 836
- losses: 520
- decisive win rate: 61.6519%
- net: +316R
- simplified PF: 1.60769
- max drawdown: 10R
- max consecutive losses: 10

## Frozen V2 forward parameters

- P-Gap price: 1.0
- Spike multiplier: 1.5
- Maximum SL distance: 10.0
- TP: 1.0R
- Setup: recovered V2 3-candle geometry
- Trigger: first later lower-low (BUY) / higher-high (SELL)
- Entry: trigger Low/High
- SL: candle before Spike Low/High
- Session filter: OFF, matching the reference V2 backtest
- Forward rolling history: 120 M1 bars
- Order mode: PENDING_LIMIT_RESEARCH
- Symbol default: XAUUSD (resolved by MT5)
- Execution scope: DEMO only
- Canonical: false

## Entry point

`scripts/run_sp2l_strategy_a_v2_forward_test_20260929.py`

The obsolete legacy wrapper `run_sp2l_author_replica_legacy_forward_test_20260928.py`
has been removed.

## Operator launch

After pulling this branch:

```powershell
& ".\.venv\Scripts\python.exe" .\scripts\run_sp2l_strategy_a_v2_forward_test_20260929.py
```

The runner sends signal/order/lifecycle results to the configured Telegram
channel and records the event ledger under:

`artifacts/forward-test/SP2L_MULTI_SYMBOL_FORWARD_EVENTS.jsonl`

This is a research/demo forward test, not a canonical Strategy A or production
authorization.
