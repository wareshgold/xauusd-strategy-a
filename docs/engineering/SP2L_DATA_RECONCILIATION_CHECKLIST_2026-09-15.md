# SP2L Data Reconciliation Checklist — 2026-09-15

## Status

`NON-CANONICAL VALIDATION CHECKLIST`

Use this checklist only when research data and MT5 data are compared after the relevant Strategy A geometry has been frozen.

## A. Identity

- [ ] Provider identified.
- [ ] MT5 broker/terminal identified.
- [ ] XAUUSD symbol mapping recorded.
- [ ] Research and MT5 date windows recorded.
- [ ] Timezone/timestamp conventions recorded.

## B. Candle construction

- [ ] Raw research granularity recorded.
- [ ] M5 derivation rule from M1 recorded, where used.
- [ ] MT5 timeframe recorded.
- [ ] Candle open/close boundary semantics compared.
- [ ] Missing bars identified.
- [ ] Duplicate bars identified.
- [ ] Out-of-order bars identified.
- [ ] Session/weekend boundary differences recorded.

## C. Price representation

- [ ] Digits/precision compared.
- [ ] Point size compared.
- [ ] Bid/ask availability compared.
- [ ] OHLC source semantics compared.
- [ ] Any price normalization documented.

## D. Historical/test modeling

- [ ] Historical coverage compared.
- [ ] MT5 Strategy Tester modeling mode recorded.
- [ ] Tick availability/modeling limitations recorded.
- [ ] Spread assumptions recorded.
- [ ] Slippage assumptions recorded, if applicable.
- [ ] Execution/fill assumptions recorded separately from strategy geometry.

## E. Reconciliation result

Classify every discrepancy as one of:

- `DATA_DIFFERENCE`
- `ADAPTER_DIFFERENCE`
- `RUNTIME_EXECUTION_DIFFERENCE`
- `UNRESOLVED`

Do not classify a discrepancy as a Strategy A rule difference unless the canonical specification and implementation evidence establish that conclusion.

## F. Governance gate

Before comparing performance:

- [ ] Canonical geometry is frozen by the separate freeze decision gate.
- [ ] No unresolved source geometry is hidden in a data adapter.
- [ ] No backtest result is being used to resolve source meaning.
- [ ] No provider-specific threshold/buffer has entered Strategy A.
- [ ] No BUY/SELL production authorization is implied by reconciliation.

If any governance item fails, stop reconciliation and record the blocker.
